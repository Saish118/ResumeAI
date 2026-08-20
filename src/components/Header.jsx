import React from 'react';
import { FileText } from 'lucide-react';

export default function Header({ activeTab = 'dashboard', onNavigate }) {
  return (
    <header className="site-header">
      <div className="container">
        <div className="header-inner">
          <a
            href="#dashboard"
            className="brand-logo"
            onClick={(e) => {
              e.preventDefault();
              if (onNavigate) onNavigate('dashboard');
            }}
          >
            <div className="brand-icon">
              <FileText size={18} />
            </div>
            <span>ResumeAI</span>
            <span className="brand-badge">v1.0</span>
          </a>

          <nav className="main-nav">
            <button
              type="button"
              className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => onNavigate && onNavigate('dashboard')}
              style={{ background: 'none', border: 'none', cursor: 'pointer' }}
            >
              Dashboard
            </button>
            <button
              type="button"
              className={`nav-link ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => onNavigate && onNavigate('history')}
              style={{ background: 'none', border: 'none', cursor: 'pointer' }}
            >
              History
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
}
