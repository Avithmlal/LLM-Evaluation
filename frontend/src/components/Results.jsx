import React, { useState, useEffect } from 'react';
import { BarChart3, Clock, DollarSign, Target, Award, Eye, RefreshCw, TrendingUp } from 'lucide-react';
import { apiService } from '../services/api';

function Results() {
    const [evaluations, setEvaluations] = useState([]);
    const [selectedEvaluation, setSelectedEvaluation] = useState(null);
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(true);
    const [resultsLoading, setResultsLoading] = useState(false);

    useEffect(() => {
        loadEvaluations();
    }, []);

    const loadEvaluations = async () => {
        try {
            const response = await apiService.getEvaluations();
            const completedEvaluations = response.data.filter(evaluation => evaluation.status === 'completed');
            setEvaluations(completedEvaluations);

            // Auto-select the latest completed evaluation
            if (completedEvaluations.length > 0 && !selectedEvaluation) {
                setSelectedEvaluation(completedEvaluations[0]);
                loadResults(completedEvaluations[0].id);
            }
        } catch (error) {
            console.error('Failed to load evaluations:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadResults = async (evaluationId) => {
        setResultsLoading(true);
        try {
            const response = await apiService.getEvaluationResults(evaluationId);
            setResults(response.data);
        } catch (error) {
            console.error('Failed to load results:', error);
            setResults(null);
        } finally {
            setResultsLoading(false);
        }
    };

    const handleEvaluationSelect = (evaluation) => {
        setSelectedEvaluation(evaluation);
        loadResults(evaluation.id);
    };

    const getScoreColor = (score) => {
        if (score >= 0.8) return 'text-green-600';
        if (score >= 0.6) return 'text-yellow-600';
        return 'text-red-600';
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 6
        }).format(amount);
    };

    const formatTime = (ms) => {
        if (ms < 1000) return `${ms.toFixed(0)}ms`;
        return `${(ms / 1000).toFixed(1)}s`;
    };

    if (loading) {
        return (
            <div className="loading">
                <div className="spinner"></div>
            </div>
        );
    }

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">
                    <BarChart3 size={28} />
                    Evaluation Results
                </h1>
                <p className="page-subtitle">
                    Analyze and compare LLM performance across different tasks and metrics
                </p>
            </div>

            {evaluations.length === 0 ? (
                <div className="card">
                    <div className="card-content text-center py-12">
                        <BarChart3 size={48} className="mx-auto text-gray-400 mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No completed evaluations</h3>
                        <p className="text-gray-500 mb-4">
                            Start an evaluation from the dashboard to see results here.
                        </p>
                        <button
                            onClick={() => window.location.href = '/'}
                            className="btn btn-primary"
                        >
                            Go to Dashboard
                        </button>
                    </div>
                </div>
            ) : (
                <>
                    {/* Evaluation Selector */}
                    <div className="card mb-6">
                        <div className="card-header">
                            <div className="flex items-center justify-between">
                                <h2 className="card-title">
                                    <Eye size={20} />
                                    Select Evaluation
                                </h2>
                                <button
                                    onClick={loadEvaluations}
                                    className="btn btn-secondary"
                                >
                                    <RefreshCw size={16} />
                                    Refresh
                                </button>
                            </div>
                        </div>
                        <div className="card-content">
                            <div className="grid grid-3">
                                {evaluations.map((evaluation) => (
                                    <button
                                        key={evaluation.id}
                                        onClick={() => handleEvaluationSelect(evaluation)}
                                        className={`p-4 border rounded-lg text-left transition-all ${selectedEvaluation?.id === evaluation.id
                                            ? 'border-blue-500 bg-blue-50'
                                            : 'border-gray-200 hover:border-gray-300'
                                            }`}
                                    >
                                        <div className="font-medium">{evaluation.name}</div>
                                        <div className="text-sm text-gray-500 mt-1">
                                            {new Date(evaluation.created_at).toLocaleDateString()}
                                        </div>
                                        <div className="text-xs text-gray-400 mt-1">
                                            ID: {evaluation.id}
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Results Display */}
                    {selectedEvaluation && (
                        <div>
                            {resultsLoading ? (
                                <div className="loading">
                                    <div className="spinner"></div>
                                </div>
                            ) : results ? (
                                <>
                                    {/* Summary Cards */}
                                    <div className="stats-grid mb-6">
                                        <div className="stat-card">
                                            <Target className="stat-icon" size={24} />
                                            <span className="stat-value">{results.summary?.total_results || 0}</span>
                                            <span className="stat-label">Total Results</span>
                                        </div>

                                        <div className="stat-card">
                                            <Award className="stat-icon" size={24} />
                                            <span className="stat-value">{results.summary?.successful_results || 0}</span>
                                            <span className="stat-label">Successful</span>
                                        </div>

                                        <div className="stat-card">
                                            <BarChart3 className="stat-icon" size={24} />
                                            <span className="stat-value">{results.summary?.categories?.length || 0}</span>
                                            <span className="stat-label">Categories</span>
                                        </div>

                                        <div className="stat-card">
                                            <TrendingUp className="stat-icon" size={24} />
                                            <span className="stat-value">{results.summary?.models?.length || 0}</span>
                                            <span className="stat-label">Models Tested</span>
                                        </div>
                                    </div>

                                    {/* Detailed Results Table */}
                                    <div className="card mb-6">
                                        <div className="card-header">
                                            <h2 className="card-title">Detailed Results</h2>
                                        </div>
                                        <div className="card-content">
                                            <div className="table-container">
                                                <table className="table">
                                                    <thead>
                                                        <tr>
                                                            <th>Model</th>
                                                            <th>Test Case</th>
                                                            <th>Category</th>
                                                            <th>Accuracy</th>
                                                            <th>Response Time</th>
                                                            <th>Cost</th>
                                                            <th>Status</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        {results.results?.map((result, index) => (
                                                            <tr key={index}>
                                                                <td>
                                                                    <div className="font-medium">{result.model_name}</div>
                                                                </td>
                                                                <td>
                                                                    <div className="font-medium text-sm">{result.test_case_name}</div>
                                                                </td>
                                                                <td>
                                                                    <span className="status-badge status-info">
                                                                        {result.category}
                                                                    </span>
                                                                </td>
                                                                <td>
                                                                    <span className={`font-bold ${getScoreColor(result.accuracy_score)}`}>
                                                                        {(result.accuracy_score * 100).toFixed(1)}%
                                                                    </span>
                                                                </td>
                                                                <td>
                                                                    <div className="flex items-center gap-1">
                                                                        <Clock size={14} />
                                                                        {formatTime(result.response_time_ms)}
                                                                    </div>
                                                                </td>
                                                                <td>
                                                                    <div className="flex items-center gap-1">
                                                                        <DollarSign size={14} />
                                                                        {formatCurrency(result.cost_usd)}
                                                                    </div>
                                                                </td>
                                                                <td>
                                                                    {result.error ? (
                                                                        <span className="status-badge status-error">Error</span>
                                                                    ) : (
                                                                        <span className="status-badge status-success">Success</span>
                                                                    )}
                                                                </td>
                                                            </tr>
                                                        ))}
                                                    </tbody>
                                                </table>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Model Performance Comparison */}
                                    <div className="card">
                                        <div className="card-header">
                                            <h2 className="card-title">Model Performance Comparison</h2>
                                        </div>
                                        <div className="card-content">
                                            {results.summary?.models && (
                                                <div className="grid grid-2">
                                                    {results.summary.models.map((modelName) => {
                                                        const modelResults = results.results?.filter(r => r.model_name === modelName) || [];
                                                        const avgAccuracy = modelResults.reduce((sum, r) => sum + r.accuracy_score, 0) / (modelResults.length || 1);
                                                        const avgTime = modelResults.reduce((sum, r) => sum + r.response_time_ms, 0) / (modelResults.length || 1);
                                                        const totalCost = modelResults.reduce((sum, r) => sum + r.cost_usd, 0);
                                                        const successRate = (modelResults.filter(r => !r.error).length / (modelResults.length || 1)) * 100;

                                                        return (
                                                            <div key={modelName} className="border rounded-lg p-4">
                                                                <h3 className="font-bold text-lg mb-3">{modelName}</h3>

                                                                <div className="space-y-3">
                                                                    <div className="flex justify-between items-center">
                                                                        <span className="text-sm text-gray">Average Accuracy</span>
                                                                        <span className={`font-bold ${getScoreColor(avgAccuracy)}`}>
                                                                            {(avgAccuracy * 100).toFixed(1)}%
                                                                        </span>
                                                                    </div>

                                                                    <div className="flex justify-between items-center">
                                                                        <span className="text-sm text-gray">Average Response Time</span>
                                                                        <span className="font-medium">{formatTime(avgTime)}</span>
                                                                    </div>

                                                                    <div className="flex justify-between items-center">
                                                                        <span className="text-sm text-gray">Total Cost</span>
                                                                        <span className="font-medium">{formatCurrency(totalCost)}</span>
                                                                    </div>

                                                                    <div className="flex justify-between items-center">
                                                                        <span className="text-sm text-gray">Success Rate</span>
                                                                        <span className={`font-bold ${getScoreColor(successRate / 100)}`}>
                                                                            {successRate.toFixed(1)}%
                                                                        </span>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <div className="card">
                                    <div className="card-content text-center py-8">
                                        <p className="text-gray-500">Failed to load results for this evaluation.</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

export default Results; 