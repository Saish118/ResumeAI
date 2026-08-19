import React from 'react';
import { Play } from 'lucide-react';

export default function AnalysisButton({ disabled, isAnalyzing, onClick }) {
  return (
    <div className="action-area">
      <button
        type="button"
        className="btn-primary-action"
        disabled={disabled || isAnalyzing}
        onClick={onClick}
      >
        {isAnalyzing ? (
          <>
            <span className="spinner" />
            <span>Analyzing Resume...</span>
          </>
        ) : (
          <>
            <Play size={16} fill="currentColor" />
            <span>Analyze Resume</span>
          </>
        )}
      </button>
    </div>
  );
}
