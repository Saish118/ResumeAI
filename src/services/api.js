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
