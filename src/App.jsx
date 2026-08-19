import React, { useState } from 'react';
import Header from './components/Header';
import HeroSection from './components/HeroSection';
import ResumeUploader from './components/ResumeUploader';
import AnalysisButton from './components/AnalysisButton';
import ResultsSection from './components/ResultsSection';
import { parseResume, predictRole, extractSkills } from './services/api';

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [hasAnalyzed, setHasAnalyzed] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setErrorMessage('');
    setHasAnalyzed(false);
    setAnalysisData(null);
  };

  const handleFileRemove = () => {
    setSelectedFile(null);
    setErrorMessage('');
    setHasAnalyzed(false);
    setAnalysisData(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile || isAnalyzing) return;

    setIsAnalyzing(true);
    setErrorMessage('');
    setHasAnalyzed(false);

    try {
      // Step 1: Parse uploaded document via FastAPI backend
      const parseData = await parseResume(selectedFile);

      if (!parseData.extracted_text || !parseData.extracted_text.trim()) {
        throw new Error('No readable text could be extracted from the uploaded document.');
      }

      // Step 2 & 3: Run Role Classification and Skill Extraction in parallel
      const [roleData, skillData] = await Promise.all([
        predictRole(parseData.extracted_text),
        extractSkills(parseData.extracted_text),
      ]);

      setAnalysisData({
        parseData,
        roleData,
        skillData,
      });
      setHasAnalyzed(true);
    } catch (err) {
      setErrorMessage(err.message || 'An unexpected error occurred during resume analysis.');
      setHasAnalyzed(false);
    } finally {
      setIsAnalyzing(false);
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

        <ResultsSection
          hasAnalyzed={hasAnalyzed}
          isAnalyzing={isAnalyzing}
          analysisData={analysisData}
        />
      </main>
    </div>
  );
}
