import React, { useState, useEffect } from 'react';
import { Database, DollarSign, Zap, CheckCircle, XCircle, Activity } from 'lucide-react';
import { apiService } from '../services/api';

function Models() {
    const [models, setModels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, active, inactive

    useEffect(() => {
        loadModels();
    }, []);

    const loadModels = async () => {
        try {
            const response = await apiService.getModels();
            setModels(response.data);
        } catch (error) {
            console.error('Failed to load models:', error);
        } finally {
            setLoading(false);
        }
    };

    const getProviderColor = (provider) => {
        const colors = {
            openai: 'bg-green-100 text-green-800',
            anthropic: 'bg-orange-100 text-orange-800',
            mock: 'bg-gray-100 text-gray-800',
            local: 'bg-blue-100 text-blue-800'
        };
        return colors[provider] || 'bg-gray-100 text-gray-800';
    };

    const getProviderIcon = (provider) => {
        switch (provider) {
            case 'openai':
                return '🤖';
            case 'anthropic':
                return '🧠';
            case 'mock':
                return '🎭';
            case 'local':
                return '💻';
            default:
                return '⚡';
        }
    };

    const filteredModels = models.filter(model => {
        if (filter === 'active') return model.is_active;
        if (filter === 'inactive') return !model.is_active;
        return true;
    });

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
                    <Database size={28} />
                    LLM Models
                </h1>
                <p className="page-subtitle">
                    Manage and monitor your Large Language Model configurations
                </p>
            </div>

            {/* Filter Controls */}
            <div className="card mb-6">
                <div className="card-content">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <span className="font-medium">Filter:</span>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setFilter('all')}
                                    className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-secondary'}`}
                                >
                                    All Models ({models.length})
                                </button>
                                <button
                                    onClick={() => setFilter('active')}
                                    className={`btn ${filter === 'active' ? 'btn-primary' : 'btn-secondary'}`}
                                >
                                    Active ({models.filter(m => m.is_active).length})
                                </button>
                                <button
                                    onClick={() => setFilter('inactive')}
                                    className={`btn ${filter === 'inactive' ? 'btn-primary' : 'btn-secondary'}`}
                                >
                                    Inactive ({models.filter(m => !m.is_active).length})
                                </button>
                            </div>
                        </div>

                        <div className="text-sm text-gray">
                            Total: {filteredModels.length} model{filteredModels.length !== 1 ? 's' : ''}
                        </div>
                    </div>
                </div>
            </div>

            {/* Models Grid */}
            <div className="grid grid-2">
                {filteredModels.map((model) => (
                    <div key={model.id} className="card">
                        <div className="card-header">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <span className="text-2xl">{getProviderIcon(model.provider)}</span>
                                    <div>
                                        <h3 className="card-title text-lg">{model.name}</h3>
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getProviderColor(model.provider)}`}>
                                            {model.provider.toUpperCase()}
                                        </span>
                                    </div>
                                </div>

                                <div className="flex items-center gap-2">
                                    {model.is_active ? (
                                        <span className="status-badge status-success">
                                            <CheckCircle size={12} />
                                            Active
                                        </span>
                                    ) : (
                                        <span className="status-badge status-error">
                                            <XCircle size={12} />
                                            Inactive
                                        </span>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="card-content">
                            <div className="space-y-4">
                                {/* Model Details */}
                                <div>
                                    <div className="flex items-center gap-2 mb-2">
                                        <Activity size={16} className="text-gray" />
                                        <span className="text-sm font-medium">Model ID</span>
                                    </div>
                                    <div className="bg-gray-50 p-2 rounded text-sm font-mono">
                                        {model.model_id}
                                    </div>
                                </div>

                                {/* Pricing & Specs */}
                                <div className="grid grid-2 gap-4">
                                    <div>
                                        <div className="flex items-center gap-2 mb-1">
                                            <DollarSign size={16} className="text-green-500" />
                                            <span className="text-sm font-medium">Cost per 1K tokens</span>
                                        </div>
                                        <div className="text-xl font-bold text-green-600">
                                            ${model.cost_per_1k_tokens.toFixed(4)}
                                        </div>
                                    </div>

                                    <div>
                                        <div className="flex items-center gap-2 mb-1">
                                            <Zap size={16} className="text-blue-500" />
                                            <span className="text-sm font-medium">Max Tokens</span>
                                        </div>
                                        <div className="text-xl font-bold text-blue-600">
                                            {model.max_tokens.toLocaleString()}
                                        </div>
                                    </div>
                                </div>

                                {/* API Endpoint */}
                                {model.api_endpoint && (
                                    <div>
                                        <div className="flex items-center gap-2 mb-2">
                                            <Database size={16} className="text-gray" />
                                            <span className="text-sm font-medium">API Endpoint</span>
                                        </div>
                                        <div className="bg-gray-50 p-2 rounded text-sm font-mono break-all">
                                            {model.api_endpoint}
                                        </div>
                                    </div>
                                )}

                                {/* Performance Indicators */}
                                <div className="border-t pt-4">
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="text-gray">Performance Tier</span>
                                        <span className={`font-medium ${model.cost_per_1k_tokens > 0.01 ? 'text-purple-600' :
                                                model.cost_per_1k_tokens > 0.005 ? 'text-blue-600' :
                                                    'text-green-600'
                                            }`}>
                                            {model.cost_per_1k_tokens > 0.01 ? 'Premium' :
                                                model.cost_per_1k_tokens > 0.005 ? 'Standard' :
                                                    'Budget'}
                                        </span>
                                    </div>

                                    <div className="flex items-center justify-between text-sm mt-1">
                                        <span className="text-gray">Context Window</span>
                                        <span className="font-medium">
                                            {model.max_tokens >= 8000 ? 'Large' :
                                                model.max_tokens >= 4000 ? 'Medium' : 'Small'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {filteredModels.length === 0 && (
                <div className="card">
                    <div className="card-content text-center py-12">
                        <Database size={48} className="mx-auto text-gray-400 mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No models found</h3>
                        <p className="text-gray-500">
                            {filter === 'all'
                                ? 'No models are configured yet.'
                                : `No ${filter} models found.`}
                        </p>
                    </div>
                </div>
            )}

            {/* Summary Stats */}
            <div className="card mt-6">
                <div className="card-header">
                    <h2 className="card-title">Model Summary</h2>
                </div>
                <div className="card-content">
                    <div className="grid grid-4">
                        <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600">
                                {models.filter(m => m.provider === 'openai').length}
                            </div>
                            <div className="text-sm text-gray">OpenAI Models</div>
                        </div>

                        <div className="text-center">
                            <div className="text-2xl font-bold text-orange-600">
                                {models.filter(m => m.provider === 'anthropic').length}
                            </div>
                            <div className="text-sm text-gray">Anthropic Models</div>
                        </div>

                        <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">
                                ${Math.min(...models.map(m => m.cost_per_1k_tokens)).toFixed(4)}
                            </div>
                            <div className="text-sm text-gray">Lowest Cost</div>
                        </div>

                        <div className="text-center">
                            <div className="text-2xl font-bold text-purple-600">
                                {Math.max(...models.map(m => m.max_tokens)).toLocaleString()}
                            </div>
                            <div className="text-sm text-gray">Max Context</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Models; 