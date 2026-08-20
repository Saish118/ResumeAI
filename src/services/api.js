/**
 * Central API Service Layer for ResumeAI FastAPI Backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Helper to handle fetch responses and extract structured error messages.
 */
async function handleResponse(response) {
  if (!response.ok) {
    let errorMessage = `Server error (${response.status})`;
    try {
      const errorData = await response.json();
      if (errorData && errorData.detail) {
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map(err => err.msg || JSON.stringify(err)).join(', ');
        }
      }
    } catch {
      // Fallback to default message if JSON parsing fails
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

/**
 * Parses uploaded resume document (PDF or DOCX).
 * Endpoint: POST /api/v1/resume/parse
 *
 * @param {File} file - Resume document file object
 * @returns {Promise<{filename: string, file_type: string, character_count: number, page_count: number|null, extracted_text: string}>}
 */
export async function parseResume(file) {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/resume/parse`, {
      method: 'POST',
      body: formData,
    });
    return await handleResponse(response);
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to connect to the backend server. Please ensure FastAPI is running at http://localhost:8000.');
    }
    throw error;
  }
}

/**
 * Predicts job role category from resume text.
 * Endpoint: POST /api/v1/role/predict
 *
 * @param {string} text - Extracted resume text
 * @returns {Promise<{predicted_role: string, confidence: number}>}
 */
export async function predictRole(text) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/role/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });
    return await handleResponse(response);
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to connect to role prediction service.');
    }
    throw error;
  }
}

/**
 * Extracts technical skills and evidence from resume text.
 * Endpoint: POST /api/v1/resume/skills
 *
 * @param {string} text - Extracted resume text
 * @returns {Promise<{skills: string[], details: Array, categories_found: string[]}>}
 */
export async function extractSkills(text) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/resume/skills`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });
    return await handleResponse(response);
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to connect to skill extraction service.');
    }
    throw error;
  }
}

/**
 * Extracts candidate work experience from resume text.
 * Endpoint: POST /api/v1/resume/experience
 *
 * @param {string} text - Extracted resume text
 * @returns {Promise<{candidate_experience_years: number|null, evidence: string[], confidence: string}>}
 */
export async function extractExperience(text) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/resume/experience`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });
    return await handleResponse(response);
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to connect to experience extraction service.');
    }
    throw error;
  }
}


/**
 * Processes raw job description text into structured job requirements.
 * Endpoint: POST /api/v1/job-description/process
 *
 * @param {string} text - Raw job description text
 * @param {string|null} [jobTitle] - Optional job title
 * @returns {Promise<{job_title: string|null, required_skills: string[], preferred_skills: string[], minimum_experience_years: number|null, requirements: Array}>}
 */
export async function processJobDescription(text, jobTitle = null) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/job-description/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text, job_title: jobTitle }),
    });
    return await handleResponse(response);
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to connect to job description processing service.');
    }
    throw error;
  }
}

/**
 * Matches candidate resume data against target job description requirements.
 * Endpoint: POST /api/v1/match
 *
 * @param {Object} resumeData - Resume input data matching ResumeDataInput schema
 * @param {Object} jobData - Job input data matching JobDataInput schema
 * @returns {Promise<{overall_score: number, matched_required_skills: string[], missing_required_skills: string[], matched_preferred_skills: string[], missing_preferred_skills: string[], experience_assessment: Object, semantic_evidence_matches: Array, summary: string}>}
 */
export async function matchResumeToJob(resumeData, jobData, resumeAnalysisId = null, jobAnalysisId = null) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/match`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        resume: resumeData,
        job: jobData,
        resume_analysis_id: resumeAnalysisId,
        job_analysis_id: jobAnalysisId,
      }),
    });
    return await handleResponse(response);
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to connect to matching engine service.');
    }
    throw error;
  }
}

/**
 * Fetches recent resume analysis history records.
 * Endpoint: GET /api/v1/history/resumes
 *
 * @param {number} [limit=50] - Number of history items to return
 * @returns {Promise<Array>}
 */
export async function getResumeHistory(limit = 50) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/history/resumes?limit=${limit}`);
    return await handleResponse(response);
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to connect to history service.');
    }
    throw error;
  }
}

/**
 * Fetches recent job description analysis history records.
 * Endpoint: GET /api/v1/history/jobs
 *
 * @param {number} [limit=50] - Number of history items to return
 * @returns {Promise<Array>}
 */
export async function getJobHistory(limit = 50) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/history/jobs?limit=${limit}`);
    return await handleResponse(response);
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to connect to history service.');
    }
    throw error;
  }
}

/**
 * Fetches recent match evaluation history records.
 * Endpoint: GET /api/v1/history/matches
 *
 * @param {number} [limit=50] - Number of history items to return
 * @returns {Promise<Array>}
 */
export async function getMatchHistory(limit = 50) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/history/matches?limit=${limit}`);
    return await handleResponse(response);
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to connect to history service.');
    }
    throw error;
  }
}

/**
 * Fetches a single detailed match evaluation record by ID.
 * Endpoint: GET /api/v1/history/matches/{matchId}
 *
 * @param {number} matchId - Database ID of match record
 * @returns {Promise<Object>}
 */
export async function getMatchHistoryDetail(matchId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/history/matches/${matchId}`);
    return await handleResponse(response);
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to connect to history service.');
    }
    throw error;
  }
}

