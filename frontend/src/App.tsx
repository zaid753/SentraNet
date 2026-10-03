import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SOCApp } from './SOCApp';
import { LandingPage } from './pages/LandingPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/soc/*" element={<SOCApp />} />
      </Routes>
    </Router>
  );
}

export default App;
