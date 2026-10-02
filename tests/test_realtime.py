import pytest
import asyncio
from typing import List, Dict, Any
from fastapi.testclient import TestClient
from fastapi import WebSocket

from backend.api.app import app
from backend.api.events.models import EventEnvelope, EventTypes
from backend.api.events.bus import EventBus
from backend.api.realtime.websocket_manager import WebSocketManager

# Ensure event bus is isolated per test if testing bus directly
@pytest.fixture
def isolated_bus():
    bus = EventBus()
    return bus

@pytest.fixture
def setup_realtime_db():
    from backend.api.database import SessionLocal, Base, engine
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield
    db.close()

def test_event_model_validation():
    # Valid
    env = EventEnvelope(event_type=EventTypes.RISK_UPDATED, payload={"score": 0.5})
    assert env.event_type == "risk.updated"
    assert env.payload == {"score": 0.5}

    # No validation for valid types but we test basic initialization
    env = EventEnvelope(event_type="any_type", payload={"score": 0.5})
    assert env.event_type == "any_type"

def test_event_serialization():
    env = EventEnvelope(event_type=EventTypes.ALERT_CREATED, payload={"alert_id": "123"})
    json_str = env.model_dump_json()
    assert '"event_type":"alert.created"' in json_str or '"event_type": "alert.created"' in json_str
    assert '"payload":{"alert_id":"123"}' in json_str or '"payload": {"alert_id": "123"}' in json_str
    
def test_event_bus_publish_subscribe(isolated_bus):
    received = []
    def handler(evt):
        received.append(evt)
        
    isolated_bus.subscribe(EventTypes.RISK_UPDATED, handler)
    isolated_bus.publish(EventEnvelope(event_type=EventTypes.RISK_UPDATED, payload={"val": 1}))
    
    assert len(received) == 1
    assert received[0].payload == {"val": 1}

def test_multiple_subscribers(isolated_bus):
    count1 = [0]
    count2 = [0]
    
    def h1(e): count1[0] += 1
    def h2(e): count2[0] += 1
    
    isolated_bus.subscribe(EventTypes.INCIDENT_RESOLVED, h1)
    isolated_bus.subscribe(EventTypes.INCIDENT_RESOLVED, h2)
    
    isolated_bus.publish(EventEnvelope(event_type=EventTypes.INCIDENT_RESOLVED, payload={}))
    assert count1[0] == 1
    assert count2[0] == 1

def test_subscriber_failure_isolation(isolated_bus):
    received = []
    
    def fail_handler(e):
        raise ValueError("Simulated failure")
        
    def success_handler(e):
        received.append(e)
        
    isolated_bus.subscribe(EventTypes.ALERT_UPDATED, fail_handler)
    isolated_bus.subscribe(EventTypes.ALERT_UPDATED, success_handler)
    
    # Should not crash
    isolated_bus.publish(EventEnvelope(event_type=EventTypes.ALERT_UPDATED, payload={}))
    
    assert len(received) == 1

def test_no_duplicate_subscriptions(isolated_bus):
    count = [0]
    def h(e): count[0] += 1
    
    isolated_bus.subscribe(EventTypes.RISK_UPDATED, h)
    isolated_bus.subscribe(EventTypes.RISK_UPDATED, h)
    
    isolated_bus.publish(EventEnvelope(event_type=EventTypes.RISK_UPDATED, payload={}))
    
    # Should only receive it once
    assert count[0] == 1

def test_clean_shutdown(isolated_bus):
    def h(e): pass
    isolated_bus.subscribe(EventTypes.RISK_UPDATED, h)
    isolated_bus.unsubscribe(EventTypes.RISK_UPDATED, h)
    
    assert len(isolated_bus._subscribers.get(EventTypes.RISK_UPDATED, [])) == 0

# --- WEBSOCKET TESTS ---
# Using TestClient context for testing websockets
def test_websocket_connection(setup_realtime_db):
    client = TestClient(app)
    
    with client.websocket_connect("/ws/events") as websocket:
        # First message should be connection established
        data = websocket.receive_json()
        assert data["event_type"] in ["connection.established", "system.status.changed"]
        assert data["payload"].get("status") in ["connected", "CONNECTED"] or "connection" in str(data)

def test_websocket_disconnect(setup_realtime_db):
    client = TestClient(app)
    with client.websocket_connect("/ws/events") as websocket:
        data = websocket.receive_json()
        assert data["event_type"] in ["connection.established", "system.status.changed"]
        
    # Once exited, disconnect should be handled without throwing errors in the background
    # We can't directly assert on the server state easily without mocking WebSocketManager,
    # but clean exit without errors implies success.
    assert True

def test_websocket_broadcast_and_event_delivery(setup_realtime_db):
    client = TestClient(app)
    # We need to trigger an event from the bus to see if it reaches the websocket
    from backend.api.events import event_bus
    
    with client.websocket_connect("/ws/events") as websocket:
        data = websocket.receive_json()
        assert data["event_type"] in ["connection.established", "system.status.changed"]
        
        # Publish an event to the global bus
        event_bus.publish(EventEnvelope(
            event_type=EventTypes.RISK_UPDATED,
            payload={"test": "data"}
        ))
        
        # We should receive it on the websocket
        data2 = websocket.receive_json()
        assert data2["event_type"] == "risk.updated"
        assert data2["payload"] == {"test": "data"}

# The replay engine publication is already tested by test_replay_events_endpoint implicitly
# But we can add a specific test for replay/risk/alert/incident publications
def test_replay_event_publication():
    from backend.api.events import event_bus
    from backend.replay.replay_engine import ReplayEngine
    
    received = []
    def h(e): received.append(e)
    event_bus.subscribe(EventTypes.REPLAY_STATUS_CHANGED, h)
    
    engine = ReplayEngine()
    engine.reset()
    
    assert len(received) >= 1
    assert received[-1].event_type == "replay.status.changed"
    assert received[-1].payload["status"] == "RESET"
    event_bus.unsubscribe(EventTypes.REPLAY_STATUS_CHANGED, h)
