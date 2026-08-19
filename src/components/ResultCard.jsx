import React from 'react';

export default function ResultCard({ title, icon: Icon, className = "col-span-6", children }) {
  return (
    <div className={`result-card ${className}`}>
      <div className="card-header">
        {Icon && <Icon className="card-icon" />}
        <h3 className="card-title">{title}</h3>
      </div>
      <div className="card-content">
        {children}
      </div>
    </div>
  );
}
