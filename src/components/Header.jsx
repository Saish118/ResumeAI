import React from 'react';
import { FileText } from 'lucide-react';

export default function Header() {
  return (
    <header className="site-header">
      <div className="container">
        <div className="header-inner">
          <a href="/" className="brand-logo">
            <div className="brand-icon">
              <FileText size={18} />
            </div>
            <span>ResumeAI</span>
            <span className="brand-badge">v1.0</span>
          </a>

          <nav className="main-nav">
            <a href="#upload" className="nav-link active">Dashboard</a>
            <a href="#features" className="nav-link">Features</a>
            <a href="#docs" className="nav-link">Docs</a>
          </nav>
        </div>
      </div>
    </header>
  );
}
