import React from 'react';
import { Briefcase, Code, Target, AlertTriangle, Lightbulb, CheckCircle2, XCircle, Award } from 'lucide-react';
import ResultCard from './ResultCard';

export default function ResultsSection({ hasAnalyzed, isAnalyzing, analysisData, matchData, isMatching }) {
  const parseData = analysisData?.parseData;
  const roleData = analysisData?.roleData;
  const skillData = analysisData?.skillData;

  const hasMatchResults = Boolean(matchData);

  return (
    <section className="results-section">
      <div className="section-header">
        <h2 className="section-title">Analysis Results</h2>
        <span className="section-status">
          {isAnalyzing
            ? 'Analyzing Document...'
            : isMatching
            ? 'Comparing Resume to Job...'
            : hasMatchResults
            ? 'Resume ↔ Job Match Analysis Complete'
            : hasAnalyzed
            ? 'Resume Parsed & Categorized'
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
          {hasMatchResults ? (
            <div style={{ textAlign: 'left' }}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '8px' }}>
                <span style={{ fontSize: '2rem', fontWeight: '800', color: 'var(--color-primary)' }}>
                  {matchData.overall_score.toFixed(1)}%
                </span>
                <span style={{ fontSize: '0.875rem', fontWeight: '600', color: 'var(--color-text-secondary)' }}>
                  Overall Fit
                </span>
              </div>
              {/* Score Bar */}
              <div style={{ width: '100%', height: '8px', backgroundColor: '#e2e8f0', borderRadius: '4px', overflow: 'hidden', marginBottom: '12px' }}>
                <div
                  style={{
                    width: `${Math.min(100, Math.max(0, matchData.overall_score))}%`,
                    height: '100%',
                    backgroundColor: matchData.overall_score >= 75 ? 'var(--color-success)' : matchData.overall_score >= 50 ? 'var(--color-primary)' : 'var(--color-danger)',
                    borderRadius: '4px',
                    transition: 'width 0.4s ease'
                  }}
                />
              </div>
              <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)', lineHeight: '1.5' }}>
                {matchData.summary}
              </p>
            </div>
          ) : hasAnalyzed ? (
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
        <ResultCard title="3. Skills Found & Matched" icon={Code} className="col-span-6">
          {hasAnalyzed ? (
            <div>
              {hasMatchResults ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {/* Matched Required Skills */}
                  <div>
                    <div style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--color-text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                      Matched Required Skills ({matchData.matched_required_skills?.length || 0})
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {matchData.matched_required_skills && matchData.matched_required_skills.length > 0 ? (
                        matchData.matched_required_skills.map((skill, idx) => (
                          <span
                            key={idx}
                            style={{
                              backgroundColor: 'var(--color-success-light)',
                              color: 'var(--color-success)',
                              border: '1px solid #bbf7d0',
                              padding: '3px 8px',
                              borderRadius: 'var(--radius-sm)',
                              fontSize: '0.8125rem',
                              fontWeight: '500',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px'
                            }}
                          >
                            <CheckCircle2 size={12} />
                            {skill}
                          </span>
                        ))
                      ) : (
                        <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>None matched</span>
                      )}
                    </div>
                  </div>

                  {/* Matched Preferred Skills */}
                  {matchData.matched_preferred_skills && matchData.matched_preferred_skills.length > 0 && (
                    <div>
                      <div style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--color-text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                        Matched Preferred Skills ({matchData.matched_preferred_skills.length})
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {matchData.matched_preferred_skills.map((skill, idx) => (
                          <span
                            key={idx}
                            style={{
                              backgroundColor: 'var(--color-primary-light)',
                              color: 'var(--color-primary)',
                              border: '1px solid #bfdbfe',
                              padding: '3px 8px',
                              borderRadius: 'var(--radius-sm)',
                              fontSize: '0.8125rem',
                              fontWeight: '500',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px'
                            }}
                          >
                            <CheckCircle2 size={12} />
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : skillData?.skills && skillData.skills.length > 0 ? (
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
          {hasMatchResults ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {/* Missing Required Skills */}
              <div>
                <div style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--color-text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                  Missing Required Skills ({matchData.missing_required_skills?.length || 0})
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {matchData.missing_required_skills && matchData.missing_required_skills.length > 0 ? (
                    matchData.missing_required_skills.map((skill, idx) => (
                      <span
                        key={idx}
                        style={{
                          backgroundColor: 'var(--color-danger-light)',
                          color: 'var(--color-danger)',
                          border: '1px solid #fecaca',
                          padding: '3px 8px',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.8125rem',
                          fontWeight: '500',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px'
                        }}
                      >
                        <XCircle size={12} />
                        {skill}
                      </span>
                    ))
                  ) : (
                    <span style={{ fontSize: '0.8125rem', color: 'var(--color-success)', fontWeight: '500' }}>
                      All required skills matched!
                    </span>
                  )}
                </div>
              </div>

              {/* Missing Preferred Skills */}
              {matchData.missing_preferred_skills && matchData.missing_preferred_skills.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--color-text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                    Missing Preferred Skills ({matchData.missing_preferred_skills.length})
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {matchData.missing_preferred_skills.map((skill, idx) => (
                      <span
                        key={idx}
                        style={{
                          backgroundColor: '#f1f5f9',
                          color: 'var(--color-text-secondary)',
                          border: '1px solid var(--color-border)',
                          padding: '3px 8px',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.8125rem',
                          fontWeight: '500'
                        }}
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : hasAnalyzed ? (
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

        {/* 5. Key Insights & Semantic Evidence */}
        <ResultCard title="5. Key Insights & Semantic Evidence" icon={Lightbulb} className="col-span-12">
          {hasAnalyzed && parseData ? (
            <div>
              {/* Document & Experience Metadata Grid */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
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
                {hasMatchResults && matchData.experience_assessment && (
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Experience Assessment</div>
                    <div style={{ fontWeight: '600', fontSize: '0.9375rem', color: matchData.experience_assessment.status === 'matched' ? 'var(--color-success)' : matchData.experience_assessment.status === 'below_requirement' ? 'var(--color-danger)' : 'var(--color-text-secondary)' }}>
                      {matchData.experience_assessment.status === 'matched'
                        ? `Matched (${matchData.experience_assessment.candidate_years || 0}y vs ${matchData.experience_assessment.required_years || 0}y req)`
                        : matchData.experience_assessment.status === 'below_requirement'
                        ? `Below req (${matchData.experience_assessment.candidate_years || 0}y vs ${matchData.experience_assessment.required_years || 0}y req)`
                        : 'Unavailable in payload'}
                    </div>
                  </div>
                )}
              </div>

              {/* Requirement-Level Semantic Evidence Matches */}
              {hasMatchResults && matchData.semantic_evidence_matches && matchData.semantic_evidence_matches.length > 0 ? (
                <div>
                  <h4 style={{ fontSize: '0.9375rem', fontWeight: '600', marginBottom: '12px', color: 'var(--color-text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Award size={16} color="var(--color-primary)" />
                    Requirement-Level Semantic Evidence Matches
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {matchData.semantic_evidence_matches.map((item, idx) => (
                      <div
                        key={idx}
                        style={{
                          fontSize: '0.875rem',
                          backgroundColor: '#ffffff',
                          padding: '12px 16px',
                          borderRadius: 'var(--radius-sm)',
                          border: '1px solid var(--color-border)',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '4px'
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontWeight: '600', color: 'var(--color-primary)' }}>
                            Requirement: {item.requirement_skill}
                          </span>
                          <span style={{ fontSize: '0.75rem', fontWeight: '600', backgroundColor: '#f1f5f9', padding: '2px 6px', borderRadius: '4px', color: 'var(--color-text-secondary)' }}>
                            Similarity: {(item.similarity_score * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.8125rem' }}>
                          <em>Job Requirement:</em> &quot;{item.requirement_evidence}&quot;
                        </div>
                        {item.best_matching_resume_evidence && (
                          <div style={{ color: 'var(--color-text-primary)', fontSize: '0.8125rem', marginTop: '2px' }}>
                            <em>Resume Evidence:</em> &quot;{item.best_matching_resume_evidence}&quot;
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ) : (skillData?.extracted_skills || skillData?.details) && (skillData.extracted_skills || skillData.details).length > 0 && (
                <div>
                  <h4 style={{ fontSize: '0.9375rem', fontWeight: '600', marginBottom: '10px', color: 'var(--color-text-primary)' }}>
                    Skill Evidence Snippets
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {(skillData.extracted_skills || skillData.details).slice(0, 5).map((detail, idx) => (
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
