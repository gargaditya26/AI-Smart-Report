import axios from 'axios';

// Same-origin by default. Vite proxies /api locally; Vercel serves the FastAPI function on the same domain.
const API_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_URL,
  timeout: 180000, // 3 minutes for OCR processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Upload file
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/v1/reports/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

// Extract lab tests
export const extractLabTests = async (sessionId) => {
  const response = await api.post(`/api/v1/analysis/extract/${sessionId}`);
  return response.data;
};

// Get lab results
export const getLabResults = async (sessionId) => {
  const response = await api.get(`/api/v1/analysis/results/${sessionId}`);
  return response.data;
};

// Update lab results
export const updateLabResults = async (sessionId, labResults) => {
  const response = await api.put(`/api/v1/analysis/results/${sessionId}`, labResults);
  return response.data;
};

// Add manual test
export const addManualTest = async (sessionId, testData) => {
  const response = await api.post(`/api/v1/analysis/add-test/${sessionId}`, testData);
  return response.data;
};

// Update test
export const updateTest = async (sessionId, testId, testData) => {
  const response = await api.put(`/api/v1/analysis/update-test/${sessionId}/${testId}`, testData);
  return response.data;
};

// Delete test
export const deleteTest = async (sessionId, testId) => {
  const response = await api.delete(`/api/v1/analysis/delete-test/${sessionId}/${testId}`);
  return response.data;
};

// Calculate organ scores
export const calculateOrganScores = async (sessionId) => {
  const response = await api.post(`/api/v1/analysis/calculate/${sessionId}`);
  return response.data;
};

// Get organ scores
export const getOrganScores = async (sessionId) => {
  const response = await api.get(`/api/v1/analysis/organ-scores/${sessionId}`);
  return response.data;
};

// Generate PDF
export const generatePDF = async (sessionId) => {
  const response = await api.post(`/api/v1/pdf/generate/${sessionId}`);
  return response.data;
};

// Get PDF URL
export const getPDFUrl = (pdfId) => {
  return `${API_URL}/api/v1/pdf/${pdfId}`;
};

// Delete PDF
export const deletePDF = async (pdfId) => {
  const response = await api.delete(`/api/v1/pdf/${pdfId}`);
  return response.data;
};

// Delete session
export const deleteSession = async (sessionId) => {
  const response = await api.delete(`/api/v1/reports/session/${sessionId}`);
  return response.data;
};

// Get reference tests
export const getReferenceTests = async () => {
  const response = await api.get('/api/v1/reference/tests');
  return response.data;
};

export default api;
