import React, { useState, useEffect } from 'react';
import { Play, TrendingUp, Database, BarChart3, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';

function Dashboard() {
    const [stats, setStats] = useState({
        models: 0,
        testCases: 0,
        categories: 0,
        evaluations: 0
    });
    const [recentEvaluations, setRecentEvaluations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [demoLoading, setDemoLoading] = useState(false);

    useEffect(() => {
        loadDashboardData();
        // Refresh data every 10 seconds
        const interval = setInterval(loadDashboardData, 10000);
        return () => clearInterval(interval);
    }, []);

    const loadDashboardData = async () => {
        try {
            const [modelsRes, testCasesRes, categoriesRes, evaluationsRes] = await Promise.all([
                apiService.getModels(),
                apiService.getTestCases(),
                apiService.getCategories(),
                apiService.getEvaluations()
            ]);

            setStats({
                models: modelsRes.data.length,
                testCases: testCasesRes.data.length,
                categories: categoriesRes.data.length,
                evaluations: evaluationsRes.data.length
            });

            setRecentEvaluations(evaluationsRes.data.slice(0, 5));
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        } finally {
            setLoading(false);
        }
    };

    const startDemoEvaluation = async () => {
        setDemoLoading(true);
        try {
            await apiService.startQuickDemo();
            // Refresh evaluations after starting demo
            setTimeout(() => {
                loadDashboardData();
                setDemoLoading(false);
            }, 2000);
        } catch (error) {
            console.error('Failed to start demo evaluation:', error);
            setDemoLoading(false);
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'completed':
                return <CheckCircle size={16} className="text-success" />;
            case 'running':
                return <Clock size={16} className="text-warning" />;
            case 'failed':
                return <AlertCircle size={16} className="text-danger" />;
            default:
                return <Clock size={16} className="text-gray" />;
        }
    };

    const getStatusBadge = (status) => {
        const baseClass = "status-badge";
        switch (status) {
            case 'completed':
                return `${baseClass} status-success`;
            case 'running':
                return `${baseClass} status-warning`;
            case 'failed':
                return `${baseClass} status-error`;
            default:
                return `${baseClass} status-info`;
        }
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
                <h1 className="page-title">🚀 LLM Evaluation Dashboard</h1>
                <p className="page-subtitle">
                    Monitor and compare Large Language Model performance across different tasks
                </p>
            </div>

            {/* Stats Grid */}
            <div className="stats-grid">
                <div className="stat-card">
                    <Database className="stat-icon" size={24} />
                    <span className="stat-value">{stats.models}</span>
                    <span className="stat-label">Active Models</span>
                </div>

                <div className="stat-card">
                    <BarChart3 className="stat-icon" size={24} />
                    <span className="stat-value">{stats.testCases}</span>
                    <span className="stat-label">Test Cases</span>
                </div>

                <div className="stat-card">
                    <TrendingUp className="stat-icon" size={24} />
                    <span className="stat-value">{stats.categories}</span>
                    <span className="stat-label">Categories</span>
                </div>

                <div className="stat-card">
                    <CheckCircle className="stat-icon" size={24} />
                    <span className="stat-value">{stats.evaluations}</span>
                    <span className="stat-label">Total Evaluations</span>
                </div>
            </div>

            <div className="grid grid-2">
                {/* Quick Actions */}
                <div className="card">
                    <div className="card-header">
                        <h2 className="card-title">
                            <Play size={20} />
                            Quick Actions
                        </h2>
                    </div>
                    <div className="card-content">
                        <p className="text-gray mb-4">
                            Start evaluating your models with our demo dataset to see real-time performance comparisons.
                        </p>

                        <button
                            onClick={startDemoEvaluation}
                            disabled={demoLoading}
                            className="btn btn-primary mb-3"
                        >
                            {demoLoading ? (
                                <>
                                    <div className="spinner" style={{ width: '16px', height: '16px' }}></div>
                                    Starting Demo...
                                </>
                            ) : (
                                <>
                                    <Play size={16} />
                                    Run Demo Evaluation
                                </>
                            )}
                        </button>

                        <div className="text-sm text-gray">
                            <p>• Evaluates all models on sample tasks</p>
                            <p>• Generates performance metrics</p>
                            <p>• Shows ranking comparisons</p>
                        </div>
                    </div>
                </div>

                {/* Recent Evaluations */}
                <div className="card">
                    <div className="card-header">
                        <h2 className="card-title">
                            <Clock size={20} />
                            Recent Evaluations
                        </h2>
                    </div>
                    <div className="card-content">
                        {recentEvaluations.length === 0 ? (
                            <p className="text-gray text-center">
                                No evaluations yet. Start a demo evaluation to see results!
                            </p>
                        ) : (
                            <div className="space-y-3">
                                {recentEvaluations.map((evaluation) => (
                                    <div key={evaluation.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                        <div className="flex items-center gap-3">
                                            {getStatusIcon(evaluation.status)}
                                            <div>
                                                <div className="font-medium">{evaluation.name}</div>
                                                <div className="text-sm text-gray">
                                                    {new Date(evaluation.created_at).toLocaleDateString()}
                                                </div>
                                            </div>
                                        </div>
                                        <span className={getStatusBadge(evaluation.status)}>
                                            {evaluation.status}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* System Overview */}
            <div className="card mt-6">
                <div className="card-header">
                    <h2 className="card-title">
                        <BarChart3 size={20} />
                        System Overview
                    </h2>
                </div>
                <div className="card-content">
                    <div className="grid grid-3">
                        <div className="text-center p-4 bg-blue-50 rounded-lg">
                            <div className="text-2xl font-bold text-blue-600 mb-2">AutoGen</div>
                            <div className="text-sm text-gray">Multi-Agent Evaluation</div>
                        </div>

                        <div className="text-center p-4 bg-green-50 rounded-lg">
                            <div className="text-2xl font-bold text-green-600 mb-2">Real-time</div>
                            <div className="text-sm text-gray">Performance Monitoring</div>
                        </div>

                        <div className="text-center p-4 bg-purple-50 rounded-lg">
                            <div className="text-2xl font-bold text-purple-600 mb-2">Multi-LLM</div>
                            <div className="text-sm text-gray">Provider Support</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Dashboard; 