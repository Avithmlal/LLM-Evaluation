# 🤖 LLM Evaluation Framework

An automated, multi-agent framework for systematic evaluation and comparison of Large Language Models across different tasks and performance metrics.

## ✨ Features

- **Multi-Agent Architecture**: AutoGen-based evaluator agents for different task categories
- **Multiple LLM Support**: OpenAI, Anthropic, and custom model providers
- **Comprehensive Evaluation**: Summarization, Q&A, and reasoning tasks
- **Performance Analytics**: Accuracy, speed, cost, and ranking analysis
- **REST API**: Full-featured API for integration and automation
- **Web Dashboard**: Interactive interface for managing evaluations

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   FastAPI        │    │   Database      │
│   (Bootstrap)   │◄──►│   Backend        │◄──►│   (SQLite)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────▼──────┐
                       │ Evaluation  │
                       │   Engine    │
                       └──────┬──────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐         ┌──────▼──────┐      ┌──────▼──────┐
   │AutoGen  │         │LLM Provider │      │Performance  │
   │Agents   │         │Factory      │      │Analytics    │
   └─────────┘         └─────────────┘      └─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or conda for package management

### Installation

1. **Clone and navigate to the project**:
```bash
cd llmEval  # You're already here
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables** (optional):
```bash
# For real API usage
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

4. **Start the application**:
```bash
python main.py
```

5. **Open your browser** and go to: `http://localhost:8000`

## 📊 Demo Usage

The framework includes mock providers that work without API keys for demonstration purposes:

1. **Start Demo Evaluation**: Click the "Start Demo Evaluation" button on the homepage
2. **View Results**: Check the evaluations list for completion status
3. **Analyze Performance**: Access detailed results via the API endpoints

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web dashboard |
| `/docs` | GET | API documentation |
| `/api/v1/models` | GET | List available models |
| `/api/v1/test-cases` | GET | List test cases |
| `/api/v1/evaluations` | POST | Start evaluation |
| `/api/v1/evaluations/{id}/results` | GET | Get results |

## 🏢 Business Value Demonstration

This POC demonstrates several key use cases:

### 1. **Model Selection Optimization**
- Compare GPT-4 vs Claude 3 vs other models
- Data-driven selection based on accuracy, speed, cost
- ROI: 20-40% cost reduction through optimal model selection

### 2. **Performance Monitoring**
- Automated evaluation pipelines
- Model drift detection
- ROI: Prevent 15-25% customer satisfaction drop

### 3. **Cost Analysis** 
- Token usage and cost tracking
- Price/performance optimization
- ROI: Immediate cost savings identification

## 🧪 Test Categories

### Summarization
- News article summarization
- Technical document condensing
- Metrics: Compression ratio, key point coverage, accuracy

### Question & Answer
- Factual questions
- Domain-specific queries  
- Metrics: Accuracy, completeness, relevance

### Reasoning
- Logical puzzles
- Mathematical problems
- Metrics: Logic validity, step-by-step clarity

## 🔧 Configuration

### Adding New Models

```python
# Add to database via API or directly:
new_model = LLMModel(
    name="Custom Model",
    provider="custom",
    model_id="custom-model-v1",
    cost_per_1k_tokens=0.01,
    max_tokens=4096
)
```

### Adding New Test Cases

```python
new_test = TestCase(
    name="Custom Test",
    category="reasoning",
    input_text="Test prompt...",
    expected_output="Expected response...",
    evaluation_criteria="Accuracy, clarity"
)
```

## 🎯 Interview Presentation Points

### Technical Excellence
- **AutoGen Integration**: Demonstrates agentic AI capabilities
- **Scalable Architecture**: Ready for AWS Lambda deployment
- **Provider Abstraction**: Supports multiple LLM providers
- **Performance Analytics**: Comprehensive metrics and ranking

### Business Impact
- **Cost Optimization**: 20-40% potential savings
- **Risk Mitigation**: Model drift detection
- **Data-Driven Decisions**: Objective model comparison
- **Operational Efficiency**: Automated evaluation pipelines

### Production Readiness
- **Error Handling**: Comprehensive error management
- **Background Processing**: Non-blocking evaluations
- **API Design**: RESTful, well-documented
- **Database Design**: Normalized, scalable schema

## 🔮 Future Enhancements

- **AWS Lambda Deployment**: Serverless scaling
- **Real-time Dashboards**: Live performance monitoring  
- **Advanced Analytics**: ML-based insights
- **Multi-modal Support**: Vision and audio evaluation
- **Custom Metrics**: Domain-specific evaluation criteria

## 📝 Project Structure

```
llmEval/
├── src/
│   ├── agents/           # AutoGen evaluator agents
│   ├── api/              # FastAPI routes and models
│   ├── database/         # SQLAlchemy models and config
│   ├── evaluation/       # Core evaluation engine
│   └── llm_providers/    # LLM provider abstractions
├── main.py               # FastAPI application entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🤝 Contributing

This is a demonstration project for interview purposes. The architecture supports easy extension:

1. **New Providers**: Implement `BaseLLMProvider`
2. **New Evaluators**: Extend `EvaluatorAgent`
3. **New Metrics**: Add to `PerformanceMetrics` model
4. **New Test Types**: Create new test categories

## 📄 License

This project is created for demonstration purposes.

---

**Built with**: Python, FastAPI, SQLAlchemy, AutoGen, Bootstrap

**Demonstrates**: Agentic AI, LLM Evaluation, Data Analytics, API Design 