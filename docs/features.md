# SENTRANET — Canonical Feature Dictionary

This document specifies the canonical network-flow feature set, mathematical derivations, data sources, and modeling categorization for the SENTRANET predictive security platform.

---

## 1. Feature Categories Overview

- **Identifiers / Context**: Retained for host grouping, graph relationships, and SOC forensics. **Excluded from continuous model feature matrices** to prevent overfitting to specific IP addresses.
- **Raw Network Flow Features**: Basic telemetry extracted directly from NetFlow/IPFIX records or PCAP flow aggregators.
- **Derived Behavior Features**: Mathematical transformations capturing transmission rates, packet sizing dynamics, and asymmetric directional intensity.
- **Temporal Window Features**: Time-bucketed aggregates capturing multi-flow volume shifts and historical sliding indicators.

---

## 2. Canonical Flow Features

### `flow_duration`
- **Description:** Total elapsed duration of the network flow from first packet to last packet.
- **Unit:** Microseconds ($\mu s$) or seconds.
- **Source:** Raw / Normalized.
- **Type:** Raw.
- **Used by Model:** Yes.
- **Temporal:** Yes (event-level duration).
- **Notes:** Zero durations are clipped to $\epsilon = 10^{-6}$ for rate calculations.

### `forward_packet_count`
- **Description:** Number of packets transmitted from source to destination.
- **Unit:** Packets (integer).
- **Source:** Raw / Normalized.
- **Type:** Raw.
- **Used by Model:** Yes.
- **Temporal:** No.
- **Notes:** Useful for detecting asymmetric probing and single-packet port scans.

### `backward_packet_count`
- **Description:** Number of response packets transmitted from destination back to source.
- **Unit:** Packets (integer).
- **Source:** Raw / Normalized.
- **Type:** Raw.
- **Used by Model:** Yes.
- **Temporal:** No.
- **Notes:** Often 0 during unanswered SYN floods or stealth scans.

### `total_packet_count`
- **Description:** Total packet volume in both directions ($\text{fwd} + \text{bwd}$).
- **Unit:** Packets (integer).
- **Source:** Derived.
- **Type:** Derived.
- **Formula:** `forward_packet_count + backward_packet_count`
- **Used by Model:** Yes.
- **Temporal:** No.

### `forward_bytes`
- **Description:** Total byte volume of packet headers and payloads in forward direction.
- **Unit:** Bytes.
- **Source:** Raw / Normalized.
- **Type:** Raw.
- **Used by Model:** Yes.
- **Temporal:** No.

### `backward_bytes`
- **Description:** Total byte volume in backward/reply direction.
- **Unit:** Bytes.
- **Source:** Raw / Normalized.
- **Type:** Raw.
- **Used by Model:** Yes.
- **Temporal:** No.

### `total_bytes`
- **Description:** Aggregate byte volume across both flow directions.
- **Unit:** Bytes.
- **Source:** Derived.
- **Type:** Derived.
- **Formula:** `forward_bytes + backward_bytes`
- **Used by Model:** Yes.
- **Temporal:** No.

### `packet_rate`
- **Description:** Frequency of packets transmitted per unit time.
- **Unit:** Packets per second.
- **Source:** Derived.
- **Type:** Derived.
- **Formula:** `total_packet_count / flow_duration`
- **Used by Model:** Yes.
- **Temporal:** Yes.
- **Notes:** High spike characterizes volumetric denial-of-service (DDoS) streams.

### `byte_rate`
- **Description:** Volume of bytes transmitted per unit time (bandwidth throughput).
- **Unit:** Bytes per second.
- **Source:** Derived.
- **Type:** Derived.
- **Formula:** `total_bytes / flow_duration`
- **Used by Model:** Yes.
- **Temporal:** Yes.

### `average_packet_size`
- **Description:** Mean size of packets in flow.
- **Unit:** Bytes per packet.
- **Source:** Derived.
- **Type:** Derived.
- **Formula:** `total_bytes / total_packet_count`
- **Used by Model:** Yes.
- **Temporal:** No.
- **Notes:** Amplification attacks (e.g. DNS/NTP) typically exhibit massive average response sizes.

### `packet_ratio`
- **Description:** Directional asymmetry ratio between forward and backward packets.
- **Unit:** Dimensionless ratio.
- **Source:** Derived.
- **Type:** Derived.
- **Formula:** `forward_packet_count / (backward_packet_count + 1e-6)`
- **Used by Model:** Yes.
- **Temporal:** No.

### `byte_ratio`
- **Description:** Directional asymmetry ratio between forward and backward payload bytes.
- **Unit:** Dimensionless ratio.
- **Source:** Derived.
- **Type:** Derived.
- **Formula:** `forward_bytes / (backward_bytes + 1e-6)`
- **Used by Model:** Yes.
- **Temporal:** No.

### `is_privileged_port`
- **Description:** Binary indicator whether target service port is in the privileged range ($< 1024$).
- **Unit:** Binary (0 or 1).
- **Source:** Derived.
- **Type:** Derived.
- **Formula:** `1 if destination_port < 1024 else 0`
- **Used by Model:** Yes.
- **Temporal:** No.
- **Notes:** Critical for scanning and service reconnaissance detection.

### `syn_flag_count`, `ack_flag_count`, `fin_flag_count`, `rst_flag_count`
- **Description:** Frequency counts of fundamental TCP control flags.
- **Unit:** Count.
- **Source:** Raw / Normalized.
- **Type:** Raw.
- **Used by Model:** Yes.
- **Temporal:** No.

---

## 3. Temporal Window Features

When time windowing is active ($T = 60\text{s}$), the following aggregate metrics represent the window:

| Feature Name | Description | Source | Temporal? |
|---|---|---|---|
| `flow_count` | Total active flows initiated or ongoing in window | Window Aggregation | Yes |
| `total_packets` | Sum of all packets in window | Window Aggregation | Yes |
| `total_bytes` | Sum of all bytes in window | Window Aggregation | Yes |
| `avg_packet_rate` | Mean packet rate across all window flows | Window Aggregation | Yes |
| `avg_byte_rate` | Mean byte rate across all window flows | Window Aggregation | Yes |
| `unique_sources` | Cardinality of distinct source IP addresses | Window Aggregation | Yes |
| `unique_destinations` | Cardinality of distinct destination IP addresses | Window Aggregation | Yes |
| `avg_packet_size` | Mean packet size across window | Window Aggregation | Yes |
| `avg_flow_duration` | Average flow lifetime across window | Window Aggregation | Yes |
| `syn_flag_count` | Sum of TCP SYN flags in window | Window Aggregation | Yes |
| `ack_flag_count` | Sum of TCP ACK flags in window | Window Aggregation | Yes |
| `privileged_port_ratio`| Fraction of flows targeting privileged ports | Window Aggregation | Yes |
| `rolling_5_flow_count` | Causal 5-window rolling average of flow volume | Rolling Context | Yes |
| `rolling_5_total_bytes`| Causal 5-window rolling average of byte volume | Rolling Context | Yes |
| `rolling_5_avg_byte_rate`| Causal 5-window rolling average throughput | Rolling Context | Yes |
| `rolling_5_unique_sources`| Causal 5-window rolling average source cardinality | Rolling Context | Yes |
