import axios from 'axios';

// Base API configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for debugging
api.interceptors.request.use(
    (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

// API service functions
export const apiService = {
    // Models
    getModels: () => api.get('/models'),

    // Test Cases
    getTestCases: () => api.get('/test-cases'),
    getCategories: () => api.get('/categories'),

    // Evaluations
    getEvaluations: () => api.get('/evaluations'),
    getEvaluation: (id) => api.get(`/evaluations/${id}`),
    startEvaluation: (data) => api.post('/evaluations', data),
    startQuickDemo: () => api.post('/evaluations/quick-demo'),

    // Results
    getEvaluationResults: (id) => api.get(`/evaluations/${id}/results`),
    getEvaluationMetrics: (id) => api.get(`/evaluations/${id}/metrics`),

    // Health check
    healthCheck: () => api.get('/'),
};

export default apiService; 