import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SOCApp } from './SOCApp';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/*" element={<SOCApp />} />
      </Routes>
    </Router>
  );
}

export default App;
