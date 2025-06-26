import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Activity, Database, BarChart3, Home } from 'lucide-react';
import Dashboard from './components/Dashboard';
import Models from './components/Models';
import Results from './components/Results';
import './App.css';

function Navigation() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-brand">
          <Activity className="nav-icon" />
          <span>LLM Evaluator</span>
        </Link>

        <div className="nav-menu">
          <Link
            to="/"
            className={`nav-link ${isActive('/') ? 'active' : ''}`}
          >
            <Home size={18} />
            <span>Dashboard</span>
          </Link>

          <Link
            to="/models"
            className={`nav-link ${isActive('/models') ? 'active' : ''}`}
          >
            <Database size={18} />
            <span>Models</span>
          </Link>

          <Link
            to="/results"
            className={`nav-link ${isActive('/results') ? 'active' : ''}`}
          >
            <BarChart3 size={18} />
            <span>Results</span>
          </Link>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/models" element={<Models />} />
            <Route path="/results" element={<Results />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
