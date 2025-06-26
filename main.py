from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import logging
import os

from src.api.routes import router
from src.database.database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LLM Evaluation Framework",
    description="Automated framework for evaluating and comparing Large Language Models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Serve static files (for frontend)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main frontend page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LLM Evaluation Framework</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="#">🤖 LLM Evaluation Framework</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/docs">API Docs</a>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="row">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">🚀 Welcome to LLM Evaluation Framework</h5>
                        </div>
                        <div class="card-body">
                            <p class="card-text">
                                This framework provides automated evaluation and comparison of Large Language Models 
                                across different tasks including summarization, Q&A, and reasoning.
                            </p>
                            
                            <h6>Key Features:</h6>
                            <ul>
                                <li><strong>Multi-Agent System:</strong> AutoGen-based evaluator agents</li>
                                <li><strong>Multiple LLM Support:</strong> OpenAI, Anthropic, and custom models</li>
                                <li><strong>Comprehensive Metrics:</strong> Accuracy, speed, cost analysis</li>
                                <li><strong>Automated Ranking:</strong> Performance-based model comparison</li>
                            </ul>

                            <div class="mt-4">
                                <button id="startDemo" class="btn btn-primary me-2">Start Demo Evaluation</button>
                                <a href="/docs" class="btn btn-outline-secondary">View API Documentation</a>
                            </div>
                        </div>
                    </div>

                    <div class="card mt-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0">📊 Recent Evaluations</h5>
                        </div>
                        <div class="card-body">
                            <div id="evaluationsList">
                                <p class="text-muted">Loading evaluations...</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">📋 System Status</h5>
                        </div>
                        <div class="card-body">
                            <div id="systemStatus">
                                <div class="d-flex justify-content-between">
                                    <span>Available Models:</span>
                                    <span id="modelCount" class="badge bg-primary">-</span>
                                </div>
                                <div class="d-flex justify-content-between mt-2">
                                    <span>Test Cases:</span>
                                    <span id="testCaseCount" class="badge bg-info">-</span>
                                </div>
                                <div class="d-flex justify-content-between mt-2">
                                    <span>Categories:</span>
                                    <span id="categoryCount" class="badge bg-success">-</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="card mt-3">
                        <div class="card-header">
                            <h5 class="card-title mb-0">🔗 Quick Links</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-grid gap-2">
                                <a href="/api/v1/models" class="btn btn-outline-primary btn-sm">View Models</a>
                                <a href="/api/v1/test-cases" class="btn btn-outline-info btn-sm">View Test Cases</a>
                                <a href="/api/v1/evaluations" class="btn btn-outline-success btn-sm">View Evaluations</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Load system status
            async function loadSystemStatus() {
                try {
                    const [modelsRes, testCasesRes, categoriesRes] = await Promise.all([
                        fetch('/api/v1/models'),
                        fetch('/api/v1/test-cases'),
                        fetch('/api/v1/categories')
                    ]);
                    
                    const models = await modelsRes.json();
                    const testCases = await testCasesRes.json();
                    const categories = await categoriesRes.json();
                    
                    document.getElementById('modelCount').textContent = models.length;
                    document.getElementById('testCaseCount').textContent = testCases.length;
                    document.getElementById('categoryCount').textContent = categories.length;
                } catch (error) {
                    console.error('Error loading system status:', error);
                }
            }

            // Load recent evaluations
            async function loadEvaluations() {
                try {
                    const response = await fetch('/api/v1/evaluations');
                    const evaluations = await response.json();
                    
                    const listEl = document.getElementById('evaluationsList');
                    if (evaluations.length === 0) {
                        listEl.innerHTML = '<p class="text-muted">No evaluations found. Start a demo evaluation to see results!</p>';
                        return;
                    }
                    
                    const html = evaluations.slice(0, 5).map(eval => `
                        <div class="border-bottom pb-2 mb-2">
                            <div class="d-flex justify-content-between">
                                <strong>${eval.name}</strong>
                                <span class="badge ${eval.status === 'completed' ? 'bg-success' : eval.status === 'running' ? 'bg-warning' : 'bg-danger'}">
                                    ${eval.status}
                                </span>
                            </div>
                            <small class="text-muted">${new Date(eval.created_at).toLocaleString()}</small>
                            ${eval.status === 'completed' ? `<br><a href="/api/v1/evaluations/${eval.id}/results" class="btn btn-sm btn-outline-primary mt-1">View Results</a>` : ''}
                        </div>
                    `).join('');
                    
                    listEl.innerHTML = html;
                } catch (error) {
                    console.error('Error loading evaluations:', error);
                    document.getElementById('evaluationsList').innerHTML = '<p class="text-danger">Error loading evaluations</p>';
                }
            }

            // Start demo evaluation
            document.getElementById('startDemo').addEventListener('click', async () => {
                const button = document.getElementById('startDemo');
                button.disabled = true;
                button.textContent = 'Starting...';
                
                try {
                    const response = await fetch('/api/v1/evaluations/quick-demo', {
                        method: 'POST'
                    });
                    const result = await response.json();
                    
                    button.textContent = 'Demo Started!';
                    button.className = 'btn btn-success me-2';
                    
                    // Refresh evaluations list after a short delay
                    setTimeout(() => {
                        loadEvaluations();
                        button.disabled = false;
                        button.textContent = 'Start Demo Evaluation';
                        button.className = 'btn btn-primary me-2';
                    }, 2000);
                    
                } catch (error) {
                    console.error('Error starting demo:', error);
                    button.disabled = false;
                    button.textContent = 'Error - Try Again';
                    button.className = 'btn btn-danger me-2';
                }
            });

            // Load data on page load
            loadSystemStatus();
            loadEvaluations();
            
            // Refresh evaluations every 10 seconds
            setInterval(loadEvaluations, 10000);
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 