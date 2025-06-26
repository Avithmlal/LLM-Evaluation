import React, { useState, useEffect } from 'react';
import { FileText, Search, Filter, Play, Eye, Edit } from 'lucide-react';
import { apiService } from '../services/api';

function TestCases() {
    const [testCases, setTestCases] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [selectedTestCase, setSelectedTestCase] = useState(null);
    const [showModal, setShowModal] = useState(false);

    useEffect(() => {
        loadTestCases();
    }, []);

    const loadTestCases = async () => {
        try {
            const response = await apiService.getTestCases();
            setTestCases(response.data);
        } catch (error) {
            console.error('Failed to load test cases:', error);
        } finally {
            setLoading(false);
        }
    };

    const categories = ['all', ...new Set(testCases.map(tc => tc.category))];

    const filteredTestCases = testCases.filter(testCase => {
        const matchesSearch = testCase.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            testCase.description.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesCategory = selectedCategory === 'all' || testCase.category === selectedCategory;
        return matchesSearch && matchesCategory;
    });

    const getCategoryColor = (category) => {
        const colors = {
            'summarization': 'bg-blue-50 text-blue-600',
            'qa': 'bg-green-50 text-green-600',
            'reasoning': 'bg-purple-50 text-purple-600',
            'default': 'bg-gray-50 text-gray-600'
        };
        return colors[category] || colors.default;
    };

    const viewTestCase = (testCase) => {
        setSelectedTestCase(testCase);
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setSelectedTestCase(null);
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
                    <FileText size={28} />
                    Test Cases
                </h1>
                <p className="page-subtitle">
                    Manage and view evaluation test cases across different categories
                </p>
            </div>

            {/* Controls */}
            <div className="card mb-6">
                <div className="card-content">
                    <div className="flex flex-wrap gap-4 items-center">
                        <div className="flex items-center gap-2">
                            <Search size={20} className="text-gray" />
                            <input
                                type="text"
                                placeholder="Search test cases..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                                style={{ minWidth: '250px' }}
                            />
                        </div>

                        <div className="flex items-center gap-2">
                            <Filter size={20} className="text-gray" />
                            <select
                                value={selectedCategory}
                                onChange={(e) => setSelectedCategory(e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                            >
                                {categories.map(category => (
                                    <option key={category} value={category}>
                                        {category === 'all' ? 'All Categories' : category.charAt(0).toUpperCase() + category.slice(1)}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="text-sm text-gray">
                            Showing {filteredTestCases.length} of {testCases.length} test cases
                        </div>
                    </div>
                </div>
            </div>

            {/* Test Cases Grid */}
            <div className="grid grid-3">
                {filteredTestCases.map((testCase) => (
                    <div key={testCase.id} className="card">
                        <div className="card-header">
                            <div className="flex items-center justify-between">
                                <h3 className="card-title text-lg">{testCase.name}</h3>
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(testCase.category)}`}>
                                    {testCase.category}
                                </span>
                            </div>
                        </div>
                        <div className="card-content">
                            <p className="text-gray mb-4" style={{ minHeight: '60px' }}>
                                {testCase.description}
                            </p>

                            <div className="space-y-2 mb-4">
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray">Difficulty:</span>
                                    <span className="font-medium">{testCase.difficulty || 'Medium'}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray">Created:</span>
                                    <span className="font-medium">
                                        {new Date(testCase.created_at).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>

                            <div className="flex gap-2">
                                <button
                                    onClick={() => viewTestCase(testCase)}
                                    className="btn btn-secondary flex-1"
                                >
                                    <Eye size={16} />
                                    View Details
                                </button>
                                <button className="btn btn-primary flex-1">
                                    <Play size={16} />
                                    Run Test
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {filteredTestCases.length === 0 && (
                <div className="text-center py-12">
                    <FileText size={48} className="text-gray-400 mx-auto mb-4" />
                    <h3 className="text-xl font-medium text-gray-900 mb-2">No test cases found</h3>
                    <p className="text-gray">
                        {searchTerm || selectedCategory !== 'all'
                            ? 'Try adjusting your search or filter criteria'
                            : 'No test cases available yet'
                        }
                    </p>
                </div>
            )}

            {/* Modal for Test Case Details */}
            {showModal && selectedTestCase && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={closeModal}>
                    <div className="bg-white rounded-lg max-w-2xl w-full m-4 max-h-90vh overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                        <div className="p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-xl font-bold">{selectedTestCase.name}</h2>
                                <button onClick={closeModal} className="text-gray-500 hover:text-gray-700">
                                    ✕
                                </button>
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <h3 className="font-medium mb-2">Description</h3>
                                    <p className="text-gray bg-gray-50 p-3 rounded-lg">{selectedTestCase.description}</p>
                                </div>

                                <div>
                                    <h3 className="font-medium mb-2">Input Text</h3>
                                    <div className="bg-gray-50 p-3 rounded-lg max-h-60 overflow-y-auto">
                                        <pre className="whitespace-pre-wrap text-sm">{selectedTestCase.input_text}</pre>
                                    </div>
                                </div>

                                {selectedTestCase.expected_output && (
                                    <div>
                                        <h3 className="font-medium mb-2">Expected Output</h3>
                                        <div className="bg-green-50 p-3 rounded-lg max-h-60 overflow-y-auto">
                                            <pre className="whitespace-pre-wrap text-sm">{selectedTestCase.expected_output}</pre>
                                        </div>
                                    </div>
                                )}

                                {selectedTestCase.evaluation_criteria && (
                                    <div>
                                        <h3 className="font-medium mb-2">Evaluation Criteria</h3>
                                        <p className="text-gray bg-blue-50 p-3 rounded-lg">{selectedTestCase.evaluation_criteria}</p>
                                    </div>
                                )}

                                <div className="flex justify-between items-center text-sm text-gray">
                                    <span>Category: <span className="font-medium">{selectedTestCase.category}</span></span>
                                    <span>Created: {new Date(selectedTestCase.created_at).toLocaleDateString()}</span>
                                </div>
                            </div>

                            <div className="flex gap-3 mt-6">
                                <button onClick={closeModal} className="btn btn-secondary flex-1">
                                    Close
                                </button>
                                <button className="btn btn-primary flex-1">
                                    <Play size={16} />
                                    Run Evaluation
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default TestCases; 