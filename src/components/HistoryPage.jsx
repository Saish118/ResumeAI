import React, { useEffect, useState } from 'react';
import {
  FileText,
  Briefcase,
  Target,
  Clock,
  ArrowLeft,
  CheckCircle2,
  XCircle,
  Award,
  AlertTriangle,
  Code,
  Calendar
} from 'lucide-react';
import {
  getResumeHistory,
  getJobHistory,
  getMatchHistory,
  getMatchHistoryDetail
} from '../services/api';
import ResultCard from './ResultCard';

/**
 * Helper to format ISO date string into readable text (e.g., Aug 20, 2026, 2:30 PM).
 */
function formatDate(dateString) {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return dateString;
  }
}

export default function HistoryPage({ onBackToDashboard }) {
  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [matches, setMatches] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Selected match detail state
  const [selectedMatchId, setSelectedMatchId] = useState(null);
  const [matchDetail, setMatchDetail] = useState(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [detailError, setDetailError] = useState(null);

  useEffect(() => {
    fetchHistoryData();
  }, []);

  const fetchHistoryData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [resumesData, jobsData, matchesData] = await Promise.all([
        getResumeHistory(),
        getJobHistory(),
        getMatchHistory()
      ]);
      setResumes(resumesData || []);
      setJobs(jobsData || []);
      setMatches(matchesData || []);
    } catch (err) {
      setError('Unable to load history. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectMatch = async (matchId) => {
    setSelectedMatchId(matchId);
    setIsLoadingDetail(true);
    setDetailError(null);
    setMatchDetail(null);
    try {
      const detail = await getMatchHistoryDetail(matchId);
      setMatchDetail(detail);
    } catch (err) {
      setDetailError('Unable to load match details. Please try again.');
    } finally {
      setIsLoadingDetail(false);
    }
  };

  const handleCloseDetail = () => {
    setSelectedMatchId(null);
    setMatchDetail(null);
    setDetailError(null);
  };

  // Render Match Detail Modal / View
  if (selectedMatchId !== null) {
    return (
      <div style={{ padding: '32px 0 64px' }}>
        {/* Navigation Back Header */}
        <div style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <button
            type="button"
            className="btn-file-select"
            onClick={handleCloseDetail}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            <ArrowLeft size={16} /> Back to History Overview
          </button>
          <span style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
            Saved Match Evaluation #{selectedMatchId}
          </span>
        </div>

        {isLoadingDetail ? (
          <div className="placeholder-box" style={{ padding: '48px', backgroundColor: 'var(--color-surface)' }}>
            <div className="spinner" style={{ margin: '0 auto 16px', borderColor: 'rgba(37, 99, 235, 0.3)', borderTopColor: 'var(--color-primary)' }} />
            <p style={{ color: 'var(--color-text-secondary)', fontWeight: '500' }}>Loading match details...</p>
          </div>
        ) : detailError ? (
          <div className="error-alert">
            <AlertTriangle size={18} />
            <span>{detailError}</span>
          </div>
        ) : matchDetail ? (
          <div className="results-grid">
            {/* Header Score Summary */}
            <ResultCard title="Overall Match Score" icon={Target} className="col-span-12">
              <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '16px', marginBottom: '16px' }}>
                <div>
                  <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--color-primary)', lineHeight: '1' }}>
                    {matchDetail.overall_score.toFixed(1)}%
                  </div>
                  <div style={{ fontSize: '0.875rem', fontWeight: '600', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                    Evaluated Fit Score
                  </div>
                </div>
                <div style={{ textAlign: 'right', fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', justifyContent: 'flex-end' }}>
                    <Calendar size={14} /> Created: {formatDate(matchDetail.created_at)}
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div style={{ width: '100%', height: '10px', backgroundColor: '#e2e8f0', borderRadius: '5px', overflow: 'hidden', marginBottom: '14px' }}>
                <div
                  style={{
                    width: `${Math.min(100, Math.max(0, matchDetail.overall_score))}%`,
                    height: '100%',
                    backgroundColor:
                      matchDetail.overall_score >= 75
                        ? 'var(--color-success)'
                        : matchDetail.overall_score >= 50
                        ? 'var(--color-primary)'
                        : 'var(--color-danger)',
                    borderRadius: '5px'
                  }}
                />
              </div>

              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-primary)', lineHeight: '1.6' }}>
                {matchDetail.summary}
              </p>
            </ResultCard>

            {/* Linked Resume Details */}
            <ResultCard title="Resume Analysis Metadata" icon={FileText} className="col-span-6">
              {matchDetail.resume_analysis ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.875rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>Filename:</span>
                    <strong style={{ color: 'var(--color-text-primary)' }}>{matchDetail.resume_analysis.filename}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>File Type:</span>
                    <span style={{ fontWeight: '500' }}>{matchDetail.resume_analysis.file_type?.toUpperCase()}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>Predicted Role:</span>
                    <strong style={{ color: 'var(--color-primary)' }}>{matchDetail.resume_analysis.predicted_role || 'N/A'}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>Candidate Experience:</span>
                    <span>
                      {matchDetail.resume_analysis.candidate_experience_years !== null && matchDetail.resume_analysis.candidate_experience_years !== undefined
                        ? `${matchDetail.resume_analysis.candidate_experience_years} years`
                        : 'Not available'}
                    </span>
                  </div>
                </div>
              ) : (
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Linked resume record no longer available.</p>
              )}
            </ResultCard>

            {/* Linked Job Details */}
            <ResultCard title="Job Description Metadata" icon={Briefcase} className="col-span-6">
              {matchDetail.job_analysis ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.875rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>Job Title:</span>
                    <strong style={{ color: 'var(--color-text-primary)' }}>{matchDetail.job_analysis.job_title || 'Untitled Job Description'}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>Required Skills Count:</span>
                    <span style={{ fontWeight: '500' }}>{matchDetail.job_analysis.required_skills?.length || 0}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>Preferred Skills Count:</span>
                    <span style={{ fontWeight: '500' }}>{matchDetail.job_analysis.preferred_skills?.length || 0}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-text-muted)' }}>Minimum Required Exp:</span>
                    <span>
                      {matchDetail.job_analysis.minimum_experience_years !== null && matchDetail.job_analysis.minimum_experience_years !== undefined
                        ? `${matchDetail.job_analysis.minimum_experience_years} years`
                        : 'Not specified'}
                    </span>
                  </div>
                </div>
              ) : (
                <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Linked job record no longer available.</p>
              )}
            </ResultCard>

            {/* Matched Skills */}
            <ResultCard title="Matched Skills" icon={CheckCircle2} className="col-span-6">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--color-text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                    Matched Required Skills ({matchDetail.matched_required_skills?.length || 0})
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {matchDetail.matched_required_skills && matchDetail.matched_required_skills.length > 0 ? (
                      matchDetail.matched_required_skills.map((skill, idx) => (
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
                          <CheckCircle2 size={12} /> {skill}
                        </span>
                      ))
                    ) : (
                      <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>None matched</span>
                    )}
                  </div>
                </div>

                {matchDetail.matched_preferred_skills && matchDetail.matched_preferred_skills.length > 0 && (
                  <div>
                    <div style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--color-text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                      Matched Preferred Skills ({matchDetail.matched_preferred_skills.length})
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {matchDetail.matched_preferred_skills.map((skill, idx) => (
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
                          <CheckCircle2 size={12} /> {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </ResultCard>

            {/* Missing Skills */}
            <ResultCard title="Missing Skills" icon={XCircle} className="col-span-6">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--color-text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                    Missing Required Skills ({matchDetail.missing_required_skills?.length || 0})
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {matchDetail.missing_required_skills && matchDetail.missing_required_skills.length > 0 ? (
                      matchDetail.missing_required_skills.map((skill, idx) => (
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
                          <XCircle size={12} /> {skill}
                        </span>
                      ))
                    ) : (
                      <span style={{ fontSize: '0.8125rem', color: 'var(--color-success)', fontWeight: '500' }}>
                        All required skills matched!
                      </span>
                    )}
                  </div>
                </div>

                {matchDetail.missing_preferred_skills && matchDetail.missing_preferred_skills.length > 0 && (
                  <div>
                    <div style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--color-text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                      Missing Preferred Skills ({matchDetail.missing_preferred_skills.length})
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {matchDetail.missing_preferred_skills.map((skill, idx) => (
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
            </ResultCard>

            {/* Semantic Evidence */}
            {matchDetail.semantic_evidence_matches && matchDetail.semantic_evidence_matches.length > 0 && (
              <ResultCard title="Semantic Evidence Matches" icon={Award} className="col-span-12">
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {matchDetail.semantic_evidence_matches.map((item, idx) => (
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
              </ResultCard>
            )}
          </div>
        ) : null}
      </div>
    );
  }

  return (
    <div style={{ padding: '32px 0 64px' }}>
      {/* Page Header */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: '800', color: 'var(--color-text-primary)', letterSpacing: '-0.025em' }}>
          Analysis & Evaluation History
        </h1>
        <p style={{ fontSize: '1rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
          View stored resume analyses, job description requirements, and candidate match evaluations persisted in PostgreSQL.
        </p>
      </div>

      {isLoading ? (
        <div className="placeholder-box" style={{ padding: '48px', backgroundColor: 'var(--color-surface)' }}>
          <div className="spinner" style={{ margin: '0 auto 16px', borderColor: 'rgba(37, 99, 235, 0.3)', borderTopColor: 'var(--color-primary)' }} />
          <p style={{ color: 'var(--color-text-secondary)', fontWeight: '500' }}>Loading your history...</p>
        </div>
      ) : error ? (
        <div className="error-alert">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '36px' }}>
          {/* Section 1: Resume Analyses */}
          <section>
            <div className="section-header">
              <h2 className="section-title" style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileText size={20} color="var(--color-primary)" />
                Resume Analyses ({resumes.length})
              </h2>
            </div>

            {resumes.length === 0 ? (
              <div className="placeholder-box">
                <p>No resume analyses yet.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {resumes.map((item) => (
                  <div
                    key={item.id}
                    className="result-card"
                    style={{ padding: '16px 20px', display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                      <div className="brand-icon" style={{ flexShrink: 0 }}>
                        <FileText size={18} />
                      </div>
                      <div>
                        <div style={{ fontSize: '1rem', fontWeight: '600', color: 'var(--color-text-primary)' }}>
                          {item.filename}
                        </div>
                        <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', display: 'flex', gap: '12px', flexWrap: 'wrap', marginTop: '2px' }}>
                          <span>Format: <strong>{item.file_type?.toUpperCase()}</strong></span>
                          {item.character_count && (
                            <span>Size: <strong>{item.character_count.toLocaleString()} chars</strong></span>
                          )}
                          <span>Created: {formatDate(item.created_at)}</span>
                        </div>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span
                        style={{
                          backgroundColor: 'var(--color-primary-light)',
                          color: 'var(--color-primary)',
                          padding: '4px 10px',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.8125rem',
                          fontWeight: '600'
                        }}
                      >
                        {item.predicted_role || 'ENGINEERING'}
                      </span>
                      <span
                        style={{
                          backgroundColor: '#f1f5f9',
                          color: 'var(--color-text-secondary)',
                          padding: '4px 10px',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.8125rem',
                          fontWeight: '500'
                        }}
                      >
                        {item.candidate_experience_years !== null && item.candidate_experience_years !== undefined
                          ? `${item.candidate_experience_years} years`
                          : 'N/A exp'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Section 2: Job Analyses */}
          <section>
            <div className="section-header">
              <h2 className="section-title" style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Briefcase size={20} color="var(--color-primary)" />
                Job Analyses ({jobs.length})
              </h2>
            </div>

            {jobs.length === 0 ? (
              <div className="placeholder-box">
                <p>No job analyses yet.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {jobs.map((item) => (
                  <div
                    key={item.id}
                    className="result-card"
                    style={{ padding: '16px 20px', display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                      <div className="brand-icon" style={{ backgroundColor: '#f0fdf4', color: 'var(--color-success)', flexShrink: 0 }}>
                        <Briefcase size={18} />
                      </div>
                      <div>
                        <div style={{ fontSize: '1rem', fontWeight: '600', color: 'var(--color-text-primary)' }}>
                          {item.job_title || 'Untitled Job Description'}
                        </div>
                        <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', display: 'flex', gap: '12px', flexWrap: 'wrap', marginTop: '2px' }}>
                          <span>Min Exp Req: <strong>{item.minimum_experience_years ? `${item.minimum_experience_years} yrs` : 'Not specified'}</strong></span>
                          <span>Created: {formatDate(item.created_at)}</span>
                        </div>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span
                        style={{
                          backgroundColor: 'var(--color-success-light)',
                          color: 'var(--color-success)',
                          border: '1px solid #bbf7d0',
                          padding: '3px 8px',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.8125rem',
                          fontWeight: '500'
                        }}
                      >
                        {item.required_skills?.length || 0} Required Skills
                      </span>
                      <span
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
                        {item.preferred_skills?.length || 0} Preferred
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Section 3: Match Analyses */}
          <section>
            <div className="section-header">
              <h2 className="section-title" style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Target size={20} color="var(--color-primary)" />
                Match Evaluation History ({matches.length})
              </h2>
            </div>

            {matches.length === 0 ? (
              <div className="placeholder-box">
                <p>No matches yet.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {matches.map((item) => (
                  <div
                    key={item.id}
                    className="result-card"
                    style={{
                      padding: '20px',
                      cursor: 'pointer',
                      transition: 'border-color 0.15s ease',
                      position: 'relative'
                    }}
                    onClick={() => handleSelectMatch(item.id)}
                    onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--color-primary)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; }}
                  >
                    <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '12px', marginBottom: '10px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span
                          style={{
                            fontSize: '1.25rem',
                            fontWeight: '800',
                            color: item.overall_score >= 75 ? 'var(--color-success)' : item.overall_score >= 50 ? 'var(--color-primary)' : 'var(--color-danger)',
                            backgroundColor: item.overall_score >= 75 ? 'var(--color-success-light)' : item.overall_score >= 50 ? 'var(--color-primary-light)' : 'var(--color-danger-light)',
                            padding: '4px 10px',
                            borderRadius: 'var(--radius-sm)',
                            lineHeight: '1'
                          }}
                        >
                          {item.overall_score.toFixed(1)}%
                        </span>
                        <div>
                          <div style={{ fontSize: '1rem', fontWeight: '700', color: 'var(--color-text-primary)' }}>
                            Job Match Evaluation #{item.id}
                          </div>
                          <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                            <span>Created: {formatDate(item.created_at)}</span>
                            {item.experience_status && (
                              <span>Status: <strong>{item.experience_status}</strong></span>
                            )}
                          </div>
                        </div>
                      </div>

                      <button
                        type="button"
                        className="btn-file-select"
                        style={{ fontSize: '0.8125rem', padding: '6px 12px' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectMatch(item.id);
                        }}
                      >
                        View Details
                      </button>
                    </div>

                    <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', lineHeight: '1.5' }}>
                      {item.summary}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
