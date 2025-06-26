from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..database.database import get_db
from ..database.models import EvaluationRun, LLMModel, TestCase, PerformanceMetrics
from ..evaluation.engine import EvaluationEngine

router = APIRouter()
evaluation_engine = EvaluationEngine()

# Pydantic models for request/response
class EvaluationRequest(BaseModel):
    name: str
    model_ids: List[int]
    test_case_ids: Optional[List[int]] = None
    categories: Optional[List[str]] = None

class EvaluationResponse(BaseModel):
    evaluation_id: int
    status: str
    total_results: int
    models_evaluated: int
    test_cases_run: int

class ModelResponse(BaseModel):
    id: int
    name: str
    provider: str
    model_id: str
    cost_per_1k_tokens: float
    is_active: bool

class TestCaseResponse(BaseModel):
    id: int
    name: str
    category: str
    difficulty_level: str

@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LLM Evaluation Framework API",
        "version": "1.0.0",
        "endpoints": {
            "models": "/models",
            "test_cases": "/test-cases",
            "evaluations": "/evaluations",
            "results": "/evaluations/{id}/results"
        }
    }

@router.get("/models", response_model=List[ModelResponse])
async def get_models(db: Session = Depends(get_db)):
    """Get all available LLM models"""
    models = db.query(LLMModel).filter(LLMModel.is_active == True).all()
    return models

@router.get("/test-cases", response_model=List[TestCaseResponse])
async def get_test_cases(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all test cases, optionally filtered by category"""
    query = db.query(TestCase)
    if category:
        query = query.filter(TestCase.category == category)
    
    test_cases = query.all()
    return test_cases

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get all available test categories"""
    categories = db.query(TestCase.category).distinct().all()
    return [cat[0] for cat in categories]

@router.post("/evaluations", response_model=EvaluationResponse)
async def start_evaluation(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a new evaluation run"""
    
    # Validate models exist
    models = db.query(LLMModel).filter(
        LLMModel.id.in_(request.model_ids),
        LLMModel.is_active == True
    ).all()
    
    if len(models) != len(request.model_ids):
        raise HTTPException(
            status_code=400,
            detail="Some specified models not found or inactive"
        )
    
    # Validate test cases if specified
    if request.test_case_ids:
        test_cases = db.query(TestCase).filter(
            TestCase.id.in_(request.test_case_ids)
        ).all()
        if len(test_cases) != len(request.test_case_ids):
            raise HTTPException(
                status_code=400,
                detail="Some specified test cases not found"
            )
    
    # Start evaluation in background
    background_tasks.add_task(
        run_evaluation_task,
        request.name,
        request.model_ids,
        request.test_case_ids,
        request.categories
    )
    
    # Return immediate response (evaluation will run in background)
    return {
        "evaluation_id": 0,  # Will be set when evaluation actually starts
        "status": "starting",
        "total_results": 0,
        "models_evaluated": len(request.model_ids),
        "test_cases_run": 0
    }

async def run_evaluation_task(
    name: str,
    model_ids: List[int],
    test_case_ids: Optional[List[int]],
    categories: Optional[List[str]]
):
    """Background task to run evaluation"""
    try:
        result = await evaluation_engine.run_evaluation(
            evaluation_name=name,
            model_ids=model_ids,
            test_case_ids=test_case_ids,
            categories=categories
        )
        print(f"Evaluation completed: {result}")
    except Exception as e:
        print(f"Evaluation failed: {e}")

@router.get("/evaluations")
async def get_evaluations(db: Session = Depends(get_db)):
    """Get all evaluation runs"""
    evaluations = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).all()
    
    return [
        {
            "id": eval_run.id,
            "name": eval_run.name,
            "description": eval_run.description,
            "status": eval_run.status,
            "created_at": eval_run.created_at.isoformat()
        }
        for eval_run in evaluations
    ]

@router.get("/evaluations/{evaluation_id}")
async def get_evaluation(evaluation_id: int, db: Session = Depends(get_db)):
    """Get evaluation run details"""
    evaluation = db.query(EvaluationRun).filter(
        EvaluationRun.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    return {
        "id": evaluation.id,
        "name": evaluation.name,
        "description": evaluation.description,
        "status": evaluation.status,
        "created_at": evaluation.created_at.isoformat()
    }

@router.get("/evaluations/{evaluation_id}/results")
async def get_evaluation_results(evaluation_id: int):
    """Get detailed results for an evaluation run"""
    try:
        results = await evaluation_engine.get_evaluation_results(evaluation_id)
        return results
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving results: {str(e)}")

@router.get("/evaluations/{evaluation_id}/metrics")
async def get_evaluation_metrics(evaluation_id: int, db: Session = Depends(get_db)):
    """Get performance metrics for an evaluation run"""
    metrics = db.query(PerformanceMetrics).filter(
        PerformanceMetrics.evaluation_run_id == evaluation_id
    ).all()
    
    if not metrics:
        raise HTTPException(status_code=404, detail="No metrics found for this evaluation")
    
    formatted_metrics = []
    for metric in metrics:
        formatted_metrics.append({
            "model_name": metric.model.name if metric.model else "Unknown",
            "category": metric.category,
            "avg_accuracy": metric.avg_accuracy,
            "avg_response_time": metric.avg_response_time,
            "total_cost": metric.total_cost,
            "total_tokens": metric.total_tokens,
            "success_rate": metric.success_rate,
            "accuracy_rank": metric.accuracy_rank,
            "speed_rank": metric.speed_rank,
            "cost_rank": metric.cost_rank,
            "overall_rank": metric.overall_rank
        })
    
    return formatted_metrics

@router.post("/evaluations/quick-demo")
async def quick_demo_evaluation(background_tasks: BackgroundTasks):
    """Start a quick demo evaluation with all models and test cases"""
    
    # This endpoint runs a demo evaluation for showcase purposes
    background_tasks.add_task(
        run_evaluation_task,
        "Quick Demo Evaluation",
        [1, 2, 3, 4],  # All default model IDs
        None,  # All test cases
        None   # All categories
    )
    
    return {
        "message": "Demo evaluation started",
        "status": "running",
        "description": "Evaluating all models on all test cases for demonstration"
    } 