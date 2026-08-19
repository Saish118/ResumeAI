import React from 'react';
import { Briefcase, Code, Target, AlertTriangle, Lightbulb, FileText, CheckCircle2 } from 'lucide-react';
import ResultCard from './ResultCard';

export default function ResultsSection({ hasAnalyzed, isAnalyzing, analysisData }) {
  const parseData = analysisData?.parseData;
  const roleData = analysisData?.roleData;
  const skillData = analysisData?.skillData;

  return (
    <section className="results-section">
      <div className="section-header">
        <h2 className="section-title">Analysis Results</h2>
        <span className="section-status">
          {isAnalyzing
            ? 'Analyzing Document...'
            : hasAnalyzed
            ? 'Analysis Complete'
            : 'Awaiting Resume Document'}
        </span>
      </div>

      <div className="results-grid">
        {/* 1. Predicted Role */}
        <ResultCard title="1. Predicted Role" icon={Briefcase} className="col-span-6">
          {hasAnalyzed && roleData ? (
            <div className="result-role-box" style={{ textAlign: 'left' }}>
              <div style={{ fontSize: '1.25rem', fontWeight: '700', color: 'var(--color-primary)', marginBottom: '6px' }}>
                {roleData.predicted_role}
              </div>
              <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
                Model confidence score: <strong>{(roleData.confidence * 100).toFixed(1)}%</strong>
              </div>
            </div>
          ) : (
            <div className="placeholder-box">
              <p>Results will appear after analysis.</p>
            </div>
          )}
        </ResultCard>

        {/* 2. Job Match Score */}
        <ResultCard title="2. Job Match Score" icon={Target} className="col-span-6">
          {hasAnalyzed ? (
            <div className="placeholder-box" style={{ backgroundColor: '#f8fafc', borderColor: '#e2e8f0' }}>
              <div style={{ fontWeight: '600', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Not available
              </div>
              <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                Target job description required to calculate match score.
              </p>
            </div>
          ) : (
            <div className="placeholder-box">
              <p>Results will appear after analysis.</p>
            </div>
          )}
        </ResultCard>

        {/* 3. Skills Found */}
        <ResultCard title="3. Skills Found" icon={Code} className="col-span-6">
          {hasAnalyzed && skillData ? (
            <div>
              {skillData.skills && skillData.skills.length > 0 ? (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {skillData.skills.map((skill, index) => (
                    <span
                      key={index}
                      style={{
                        backgroundColor: 'var(--color-primary-light)',
                        color: 'var(--color-primary)',
                        border: '1px solid #bfdbfe',
                        padding: '4px 10px',
                        borderRadius: 'var(--radius-sm)',
                        fontSize: '0.875rem',
                        fontWeight: '500',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}
                    >
                      <CheckCircle2 size={13} />
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <div className="placeholder-box">
                  <p>No known technical skills detected in taxonomy baseline.</p>
                </div>
              )}
            </div>
          ) : (
            <div className="placeholder-box">
              <p>Results will appear after analysis.</p>
            </div>
          )}
        </ResultCard>

        {/* 4. Missing Skills */}
        <ResultCard title="4. Missing Skills" icon={AlertTriangle} className="col-span-6">
          {hasAnalyzed ? (
            <div className="placeholder-box" style={{ backgroundColor: '#f8fafc', borderColor: '#e2e8f0' }}>
              <div style={{ fontWeight: '600', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                Not available
              </div>
              <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                Target job description required to analyze missing skills.
              </p>
            </div>
          ) : (
            <div className="placeholder-box">
              <p>Results will appear after analysis.</p>
            </div>
          )}
        </ResultCard>

        {/* 5. Key Insights & Evidence */}
        <ResultCard title="5. Key Insights & Document Metadata" icon={Lightbulb} className="col-span-12">
          {hasAnalyzed && parseData ? (
            <div style={{ textTransform: 'none' }}>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
                  gap: '16px',
                  marginBottom: '20px',
                  backgroundColor: '#f8fafc',
                  padding: '16px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--color-border)'
                }}
              >
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Document File</div>
                  <div style={{ fontWeight: '600', fontSize: '0.9375rem', color: 'var(--color-text-primary)' }}>{parseData.filename}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Format</div>
                  <div style={{ fontWeight: '600', fontSize: '0.9375rem', color: 'var(--color-text-primary)' }}>{parseData.file_type?.toUpperCase()}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Character Count</div>
                  <div style={{ fontWeight: '600', fontSize: '0.9375rem', color: 'var(--color-text-primary)' }}>{parseData.character_count?.toLocaleString()} chars</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Page Count</div>
                  <div style={{ fontWeight: '600', fontSize: '0.9375rem', color: 'var(--color-text-primary)' }}>{parseData.page_count ?? 'N/A (DOCX)'}</div>
                </div>
              </div>

              {skillData?.details && skillData.details.length > 0 && (
                <div>
                  <h4 style={{ fontSize: '0.9375rem', fontWeight: '600', marginBottom: '10px', color: 'var(--color-text-primary)' }}>
                    Skill Evidence Snippets
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {skillData.details.slice(0, 5).map((detail, idx) => (
                      <div
                        key={idx}
                        style={{
                          fontSize: '0.875rem',
                          backgroundColor: '#ffffff',
                          padding: '10px 14px',
                          borderRadius: 'var(--radius-sm)',
                          border: '1px solid var(--color-border)'
                        }}
                      >
                        <strong style={{ color: 'var(--color-primary)' }}>{detail.skill}</strong>: &quot;{detail.evidence}&quot;
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="placeholder-box">
              <p>Results will appear after analysis.</p>
            </div>
          )}
        </ResultCard>
      </div>
    </section>
  );
}
