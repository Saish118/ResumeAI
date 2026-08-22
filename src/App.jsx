import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import ResumeUploader from './components/ResumeUploader';
import AnalysisButton from './components/AnalysisButton';
import JobDescriptionInput from './components/JobDescriptionInput';
import ResultsSection from './components/ResultsSection';
import HistoryPage from './components/HistoryPage';
import {
  parseResume,
  predictRole,
  extractSkills,
  extractExperience,
  processJobDescription,
  matchResumeToJob,
  getLatestAnalysisContext
} from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedFile, setSelectedFile] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [hasAnalyzed, setHasAnalyzed] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);

  // Target Job Description & Matching state
  const [jobText, setJobText] = useState('');
  const [isMatching, setIsMatching] = useState(false);
  const [matchData, setMatchData] = useState(null);
  const [matchError, setMatchError] = useState('');

  // Persisted Analysis Restoration state
  const [isRestored, setIsRestored] = useState(false);
  const [restoredFilename, setRestoredFilename] = useState('');

  // Restore latest analysis from PostgreSQL history on startup
  useEffect(() => {
    async function restoreLatestContext() {
      try {
        const latest = await getLatestAnalysisContext();
        if (!latest) return;

        const res = latest.resumeAnalysis;
        const job = latest.jobAnalysis;
        const match = latest.matchData;

        if (res) {
          let skillData = { skills: [], details: [], categories_found: [] };
          let experienceData = {
            candidate_experience_years: res.candidate_experience_years ?? null,
            evidence: [],
            confidence: 'medium'
          };

          if (res.extracted_text && res.extracted_text.trim()) {
            try {
              const [extractedSkills, extractedExp] = await Promise.all([
                extractSkills(res.extracted_text),
                extractExperience(res.extracted_text)
              ]);
              if (extractedSkills) skillData = extractedSkills;
              if (extractedExp) experienceData = extractedExp;
            } catch {
              // Fallback if re-extraction fails
            }
          }

          if ((!skillData.skills || skillData.skills.length === 0) && match) {
            const allMatchedSkills = Array.from(new Set([
              ...(match.matched_required_skills || []),
              ...(match.matched_preferred_skills || [])
            ]));
            skillData = { skills: allMatchedSkills, details: [], categories_found: [] };
          }

          const parseData = {
            id: res.id,
            filename: res.filename,
            file_type: res.file_type,
            character_count: res.character_count,
            page_count: res.page_count,
            extracted_text: res.extracted_text || ''
          };

          const roleData = {
            predicted_role: res.predicted_role || 'Unknown',
            confidence: res.role_model_score ?? null
          };

          setAnalysisData({
            parseData,
            roleData,
            skillData,
            experienceData
          });
          setHasAnalyzed(true);
          setIsRestored(true);
          setRestoredFilename(res.filename);
        }

        if (job && job.job_description) {
          setJobText(job.job_description);
          if (!res) {
            setIsRestored(true);
            setRestoredFilename('Job Description');
          }
        }

        if (match && match.overall_score !== undefined) {
          setMatchData(match);
        }
      } catch (err) {
        console.warn('Analysis restoration failed:', err);
      }
    }

    restoreLatestContext();
  }, []);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setErrorMessage('');
    setHasAnalyzed(false);
    setAnalysisData(null);
    setMatchData(null);
    setMatchError('');
    setIsRestored(false);
    setRestoredFilename('');
  };

  const handleFileRemove = () => {
    setSelectedFile(null);
    setErrorMessage('');
    setHasAnalyzed(false);
    setAnalysisData(null);
    setMatchData(null);
    setMatchError('');
    setIsRestored(false);
    setRestoredFilename('');
  };

  const handleClearRestored = () => {
    setSelectedFile(null);
    setErrorMessage('');
    setHasAnalyzed(false);
    setAnalysisData(null);
    setJobText('');
    setMatchData(null);
    setMatchError('');
    setIsRestored(false);
    setRestoredFilename('');
  };

  const handleAnalyze = async () => {
    if (!selectedFile || isAnalyzing) return;

    setIsAnalyzing(true);
    setErrorMessage('');
    setHasAnalyzed(false);
    setMatchData(null);
    setMatchError('');
    setIsRestored(false);
    setRestoredFilename('');

    try {
      // Step 1: Parse uploaded document via FastAPI backend
      const parseData = await parseResume(selectedFile);

      if (!parseData.extracted_text || !parseData.extracted_text.trim()) {
        throw new Error('No readable text could be extracted from the uploaded document.');
      }

      // Step 2, 3 & 4: Run Role Classification, Skill Extraction, and Experience Extraction in parallel
      const [roleData, skillData, experienceData] = await Promise.all([
        predictRole(parseData.extracted_text),
        extractSkills(parseData.extracted_text),
        extractExperience(parseData.extracted_text),
      ]);

      setAnalysisData({
        parseData,
        roleData,
        skillData,
        experienceData,
      });
      setHasAnalyzed(true);
    } catch (err) {
      setErrorMessage(err.message || 'An unexpected error occurred during resume analysis.');
      setHasAnalyzed(false);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleMatchJob = async () => {
    if (!hasAnalyzed || !analysisData || !jobText.trim() || isMatching) return;

    setIsMatching(true);
    setMatchError('');
    setMatchData(null);

    try {
      // Step 1: Process raw job description text via FastAPI backend
      const processedJob = await processJobDescription(jobText.trim());

      // Step 2: Build ResumeDataInput and JobDataInput matching backend schema
      const resumeInput = {
        skills: analysisData.skillData.skills || [],
        extracted_skills: analysisData.skillData.extracted_skills || analysisData.skillData.details || [],
        candidate_experience_years: analysisData.experienceData?.candidate_experience_years ?? null,
        raw_text: analysisData.parseData?.extracted_text || null,
      };

      const jobInput = {
        job_title: processedJob.job_title || null,
        required_skills: processedJob.required_skills || [],
        preferred_skills: processedJob.preferred_skills || [],
        minimum_experience_years: processedJob.minimum_experience_years || null,
        requirements: processedJob.requirements || [],
      };

      // Step 3: Compute match analysis via FastAPI matching engine with database IDs
      const matchResult = await matchResumeToJob(
        resumeInput,
        jobInput,
        analysisData.parseData?.id || null,
        processedJob.id || null
      );
      setMatchData(matchResult);
    } catch (err) {
      setMatchError(err.message || 'An unexpected error occurred during job match analysis.');
    } finally {
      setIsMatching(false);
    }
  };

  return (
    <div className="app-shell">
      <Header activeTab={activeTab} onNavigate={setActiveTab} />

      <main className="container">
        {activeTab === 'history' ? (
          <HistoryPage onBackToDashboard={() => setActiveTab('dashboard')} />
        ) : (
          <>
            <HeroSection />

            <div className="upload-container">
              <ResumeUploader
                selectedFile={selectedFile}
                onFileSelect={handleFileSelect}
                onFileRemove={handleFileRemove}
                errorMessage={errorMessage}
                setErrorMessage={setErrorMessage}
                isRestored={isRestored}
                restoredFilename={restoredFilename}
                onClearRestored={handleClearRestored}
              />

              <AnalysisButton
                disabled={(!selectedFile && !isRestored) || Boolean(errorMessage)}
                isAnalyzing={isAnalyzing}
                onClick={handleAnalyze}
              />
            </div>

            <JobDescriptionInput
              jobText={jobText}
              setJobText={setJobText}
              onMatchJob={handleMatchJob}
              hasAnalyzed={hasAnalyzed}
              isMatching={isMatching}
              errorMessage={matchError}
              setErrorMessage={setMatchError}
            />

            <ResultsSection
              hasAnalyzed={hasAnalyzed}
              isAnalyzing={isAnalyzing}
              analysisData={analysisData}
              matchData={matchData}
              matchError={matchError}
              isMatching={isMatching}
            />
          </>
        )}
      </main>
    </div>
  );
}

