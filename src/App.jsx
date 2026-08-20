import React, { useState } from 'react';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import ResumeUploader from './components/ResumeUploader';
import AnalysisButton from './components/AnalysisButton';
import JobDescriptionInput from './components/JobDescriptionInput';
import ResultsSection from './components/ResultsSection';
import { parseResume, predictRole, extractSkills, extractExperience, processJobDescription, matchResumeToJob } from './services/api';

export default function App() {
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

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setErrorMessage('');
    setHasAnalyzed(false);
    setAnalysisData(null);
    setMatchData(null);
    setMatchError('');
  };

  const handleFileRemove = () => {
    setSelectedFile(null);
    setErrorMessage('');
    setHasAnalyzed(false);
    setAnalysisData(null);
    setMatchData(null);
    setMatchError('');
  };

  const handleAnalyze = async () => {
    if (!selectedFile || isAnalyzing) return;

    setIsAnalyzing(true);
    setErrorMessage('');
    setHasAnalyzed(false);
    setMatchData(null);
    setMatchError('');

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

    try {
      // Step 1: Process raw job description text via FastAPI backend
      const processedJob = await processJobDescription(jobText.trim());

      // Step 2: Build ResumeDataInput and JobDataInput matching backend schema
      const resumeInput = {
        skills: analysisData.skillData.skills || [],
        extracted_skills: analysisData.skillData.extracted_skills || analysisData.skillData.details || [],
        candidate_experience_years: analysisData.experienceData?.candidate_experience_years ?? null,
      };

      const jobInput = {
        job_title: processedJob.job_title || null,
        required_skills: processedJob.required_skills || [],
        preferred_skills: processedJob.preferred_skills || [],
        minimum_experience_years: processedJob.minimum_experience_years || null,
        requirements: processedJob.requirements || [],
      };

      // Step 3: Compute match analysis via FastAPI matching engine
      const matchResult = await matchResumeToJob(resumeInput, jobInput);
      setMatchData(matchResult);
    } catch (err) {
      setMatchError(err.message || 'An unexpected error occurred during job match analysis.');
    } finally {
      setIsMatching(false);
    }
  };

  return (
    <div className="app-shell">
      <Header />

      <main className="container">
        <HeroSection />

        <div className="upload-container">
          <ResumeUploader
            selectedFile={selectedFile}
            onFileSelect={handleFileSelect}
            onFileRemove={handleFileRemove}
            errorMessage={errorMessage}
            setErrorMessage={setErrorMessage}
          />

          <AnalysisButton
            disabled={!selectedFile || Boolean(errorMessage)}
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
          isMatching={isMatching}
        />
      </main>
    </div>
  );
}
