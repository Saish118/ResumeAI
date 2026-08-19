import React from 'react';
import { Target, Trash2, AlertCircle, Play } from 'lucide-react';

export default function JobDescriptionInput({
  jobText,
  setJobText,
  onMatchJob,
  hasAnalyzed,
  isMatching,
  errorMessage,
  setErrorMessage
}) {
  const handleTextChange = (e) => {
    setJobText(e.target.value);
    if (errorMessage) setErrorMessage('');
  };

  const handleClear = () => {
    setJobText('');
    if (errorMessage) setErrorMessage('');
  };

  const isButtonDisabled = !hasAnalyzed || !jobText.trim() || isMatching;

  return (
    <div className="uploader-card" id="target-job" style={{ marginTop: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div className="brand-icon" style={{ backgroundColor: '#eff6ff', color: 'var(--color-primary)' }}>
            <Target size={18} />
          </div>
          <h3 style={{ fontSize: '1.1875rem', fontWeight: '600', color: 'var(--color-text-primary)' }}>
            Target Job Description
          </h3>
        </div>

        {jobText.trim() && (
          <button
            type="button"
            className="btn-remove-file"
            onClick={handleClear}
            disabled={isMatching}
          >
            <Trash2 size={15} />
            <span>Clear</span>
          </button>
        )}
      </div>

      {errorMessage && (
        <div className="error-alert" role="alert">
          <AlertCircle size={18} />
          <span>{errorMessage}</span>
        </div>
      )}

      <div style={{ position: 'relative' }}>
        <textarea
          rows={6}
          placeholder="Paste the job description here..."
          value={jobText}
          onChange={handleTextChange}
          disabled={isMatching}
          style={{
            width: '100%',
            padding: '14px 16px',
            fontSize: '0.9375rem',
            fontFamily: 'var(--font-family)',
            color: 'var(--color-text-primary)',
            backgroundColor: '#fafafa',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            resize: 'vertical',
            outline: 'none',
            lineHeight: '1.5'
          }}
        />
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginTop: '8px',
            fontSize: '0.8125rem',
            color: 'var(--color-text-muted)'
          }}
        >
          <span>
            {!hasAnalyzed
              ? 'Upload & analyze a resume document first to enable job matching'
              : 'Paste target requirements to compare candidate skills & experience fit'}
          </span>
          <span>{jobText.length.toLocaleString()} characters</span>
        </div>
      </div>

      <div className="action-area" style={{ marginTop: '20px' }}>
        <button
          type="button"
          className="btn-primary-action"
          disabled={isButtonDisabled}
          onClick={onMatchJob}
        >
          {isMatching ? (
            <>
              <span className="spinner" />
              <span>Analyzing Job Match...</span>
            </>
          ) : (
            <>
              <Play size={16} fill="currentColor" />
              <span>Analyze Job Match</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
