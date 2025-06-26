import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..database.database import SessionLocal
from ..database.models import EvaluationRun, EvaluationResult, LLMModel, TestCase, PerformanceMetrics
from ..llm_providers.provider_factory import LLMProviderFactory
from ..agents.evaluator_agents import SummarizationEvaluator, QAEvaluator, ReasoningEvaluator, AnalystAgent

logger = logging.getLogger(__name__)

class EvaluationEngine:
    """Core engine for orchestrating LLM evaluations"""
    
    def __init__(self):
        self.evaluators = {
            "summarization": SummarizationEvaluator(),
            "qa": QAEvaluator(), 
            "reasoning": ReasoningEvaluator()
        }
        self.analyst = AnalystAgent()
    
    async def run_evaluation(self, 
                           evaluation_name: str,
                           model_ids: List[int],
                           test_case_ids: Optional[List[int]] = None,
                           categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run complete evaluation across specified models and test cases"""
        
        db = SessionLocal()
        try:
            # Create evaluation run record
            eval_run = EvaluationRun(
                name=evaluation_name,
                description=f"Evaluation of {len(model_ids)} models",
                status="running"
            )
            db.add(eval_run)
            db.commit()
            db.refresh(eval_run)
            
            logger.info(f"Started evaluation run: {evaluation_name} (ID: {eval_run.id})")
            
            # Get models and test cases
            models = db.query(LLMModel).filter(
                LLMModel.id.in_(model_ids),
                LLMModel.is_active == True
            ).all()
            
            query = db.query(TestCase)
            if test_case_ids:
                query = query.filter(TestCase.id.in_(test_case_ids))
            if categories:
                query = query.filter(TestCase.category.in_(categories))
            
            test_cases = query.all()
            
            if not models:
                raise ValueError("No active models found for evaluation")
            if not test_cases:
                raise ValueError("No test cases found for evaluation")
            
            logger.info(f"Evaluating {len(models)} models on {len(test_cases)} test cases")
            
            # Run evaluations
            all_results = []
            for model in models:
                for test_case in test_cases:
                    try:
                        result = await self._evaluate_single_case(
                            eval_run.id, model, test_case, db
                        )
                        all_results.append(result)
                    except Exception as e:
                        logger.error(f"Error evaluating {model.name} on {test_case.name}: {e}")
                        # Create error result
                        error_result = EvaluationResult(
                            evaluation_run_id=eval_run.id,
                            model_id=model.id,
                            test_case_id=test_case.id,
                            model_output="",
                            accuracy_score=0.0,
                            response_time_ms=0.0,
                            tokens_used=0,
                            cost_usd=0.0,
                            error_message=str(e)
                        )
                        db.add(error_result)
                        all_results.append(error_result)
            
            # Generate performance metrics
            await self._generate_performance_metrics(eval_run.id, models, db)
            
            # Update evaluation status
            eval_run.status = "completed"
            db.commit()
            
            logger.info(f"Completed evaluation run: {evaluation_name}")
            
            return {
                "evaluation_id": eval_run.id,
                "status": "completed",
                "total_results": len(all_results),
                "models_evaluated": len(models),
                "test_cases_run": len(test_cases)
            }
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            if 'eval_run' in locals():
                eval_run.status = "failed"
                db.commit()
            raise
        finally:
            db.close()
    
    async def _evaluate_single_case(self, 
                                   eval_run_id: int,
                                   model: LLMModel,
                                   test_case: TestCase,
                                   db) -> EvaluationResult:
        """Evaluate a single test case with a single model"""
        
        # Create LLM provider
        model_config = {
            "name": model.name,
            "provider": model.provider,
            "model_id": model.model_id,
            "cost_per_1k_tokens": model.cost_per_1k_tokens,
            "max_tokens": model.max_tokens
        }
        
        provider = LLMProviderFactory.create_provider(model_config)
        
        # Generate model response
        llm_response = await provider.generate_completion(test_case.input_text)
        
        # Get appropriate evaluator
        evaluator = self.evaluators.get(test_case.category)
        if not evaluator:
            raise ValueError(f"No evaluator found for category: {test_case.category}")
        
        # Evaluate response
        evaluation = await evaluator.evaluate_response(
            {
                "input_text": test_case.input_text,
                "expected_output": test_case.expected_output,
                "category": test_case.category,
                "evaluation_criteria": test_case.evaluation_criteria
            },
            llm_response.content
        )
        
        # Create result record
        result = EvaluationResult(
            evaluation_run_id=eval_run_id,
            model_id=model.id,
            test_case_id=test_case.id,
            model_output=llm_response.content,
            accuracy_score=evaluation["score"],
            response_time_ms=llm_response.response_time_ms,
            tokens_used=llm_response.tokens_used,
            cost_usd=llm_response.cost_usd,
            error_message=llm_response.error,
            agent_feedback=evaluation["feedback"]
        )
        
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return result
    
    async def _generate_performance_metrics(self, 
                                          eval_run_id: int,
                                          models: List[LLMModel],
                                          db) -> None:
        """Generate aggregated performance metrics"""
        
        # Get all results for this evaluation run
        results = db.query(EvaluationResult).filter(
            EvaluationResult.evaluation_run_id == eval_run_id
        ).all()
        
        # Group by model and category
        model_category_stats = {}
        
        for result in results:
            model_id = result.model_id
            category = result.test_case.category
            
            key = (model_id, category)
            if key not in model_category_stats:
                model_category_stats[key] = {
                    "scores": [],
                    "response_times": [],
                    "costs": [],
                    "tokens": [],
                    "success_count": 0,
                    "total_count": 0
                }
            
            stats = model_category_stats[key]
            stats["total_count"] += 1
            
            if not result.error_message:
                stats["success_count"] += 1
                stats["scores"].append(result.accuracy_score)
                stats["response_times"].append(result.response_time_ms)
                stats["costs"].append(result.cost_usd)
                stats["tokens"].append(result.tokens_used)
        
        # Calculate and store metrics
        for (model_id, category), stats in model_category_stats.items():
            if stats["scores"]:
                avg_accuracy = sum(stats["scores"]) / len(stats["scores"])
                avg_response_time = sum(stats["response_times"]) / len(stats["response_times"])
                total_cost = sum(stats["costs"])
                total_tokens = sum(stats["tokens"])
            else:
                avg_accuracy = 0.0
                avg_response_time = 0.0
                total_cost = 0.0
                total_tokens = 0
            
            success_rate = stats["success_count"] / stats["total_count"]
            
            metric = PerformanceMetrics(
                evaluation_run_id=eval_run_id,
                model_id=model_id,
                category=category,
                avg_accuracy=avg_accuracy,
                avg_response_time=avg_response_time,
                total_cost=total_cost,
                total_tokens=total_tokens,
                success_rate=success_rate
            )
            
            db.add(metric)
        
        # Calculate overall metrics (across all categories)
        for model in models:
            model_results = [r for r in results if r.model_id == model.id]
            
            if model_results:
                successful_results = [r for r in model_results if not r.error_message]
                
                if successful_results:
                    avg_accuracy = sum(r.accuracy_score for r in successful_results) / len(successful_results)
                    avg_response_time = sum(r.response_time_ms for r in successful_results) / len(successful_results)
                    total_cost = sum(r.cost_usd for r in successful_results)
                    total_tokens = sum(r.tokens_used for r in successful_results)
                else:
                    avg_accuracy = 0.0
                    avg_response_time = 0.0
                    total_cost = 0.0
                    total_tokens = 0
                
                success_rate = len(successful_results) / len(model_results)
                
                overall_metric = PerformanceMetrics(
                    evaluation_run_id=eval_run_id,
                    model_id=model.id,
                    category="overall",
                    avg_accuracy=avg_accuracy,
                    avg_response_time=avg_response_time,
                    total_cost=total_cost,
                    total_tokens=total_tokens,
                    success_rate=success_rate
                )
                
                db.add(overall_metric)
        
        # Calculate rankings
        self._calculate_rankings(eval_run_id, db)
        
        db.commit()
    
    def _calculate_rankings(self, eval_run_id: int, db) -> None:
        """Calculate performance rankings for models"""
        
        # Get all metrics for this evaluation
        metrics = db.query(PerformanceMetrics).filter(
            PerformanceMetrics.evaluation_run_id == eval_run_id
        ).all()
        
        # Group by category
        category_metrics = {}
        for metric in metrics:
            category = metric.category
            if category not in category_metrics:
                category_metrics[category] = []
            category_metrics[category].append(metric)
        
        # Calculate rankings for each category
        for category, cat_metrics in category_metrics.items():
            # Sort by accuracy (descending)
            sorted_by_accuracy = sorted(cat_metrics, key=lambda x: x.avg_accuracy, reverse=True)
            for rank, metric in enumerate(sorted_by_accuracy, 1):
                metric.accuracy_rank = rank
            
            # Sort by speed (ascending - faster is better)
            sorted_by_speed = sorted(cat_metrics, key=lambda x: x.avg_response_time)
            for rank, metric in enumerate(sorted_by_speed, 1):
                metric.speed_rank = rank
            
            # Sort by cost (ascending - cheaper is better)
            sorted_by_cost = sorted(cat_metrics, key=lambda x: x.total_cost)
            for rank, metric in enumerate(sorted_by_cost, 1):
                metric.cost_rank = rank
            
            # Calculate overall rank (weighted combination)
            for metric in cat_metrics:
                # Simple weighted ranking: accuracy (50%), speed (25%), cost (25%)
                overall_score = (
                    (len(cat_metrics) - metric.accuracy_rank + 1) * 0.5 +
                    (len(cat_metrics) - metric.speed_rank + 1) * 0.25 +
                    (len(cat_metrics) - metric.cost_rank + 1) * 0.25
                )
                metric.overall_rank = overall_score
            
            # Sort by overall score and assign ranks
            sorted_by_overall = sorted(cat_metrics, key=lambda x: x.overall_rank, reverse=True)
            for rank, metric in enumerate(sorted_by_overall, 1):
                metric.overall_rank = rank
    
    async def get_evaluation_results(self, evaluation_id: int) -> Dict[str, Any]:
        """Get detailed results for an evaluation run"""
        
        db = SessionLocal()
        try:
            # Get evaluation run
            eval_run = db.query(EvaluationRun).filter(
                EvaluationRun.id == evaluation_id
            ).first()
            
            if not eval_run:
                raise ValueError(f"Evaluation run {evaluation_id} not found")
            
            # Get results
            results = db.query(EvaluationResult).filter(
                EvaluationResult.evaluation_run_id == evaluation_id
            ).all()
            
            # Get performance metrics
            metrics = db.query(PerformanceMetrics).filter(
                PerformanceMetrics.evaluation_run_id == evaluation_id
            ).all()
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "model_name": result.model.name,
                    "test_case_name": result.test_case.name,
                    "category": result.test_case.category,
                    "accuracy_score": result.accuracy_score,
                    "response_time_ms": result.response_time_ms,
                    "cost_usd": result.cost_usd,
                    "tokens_used": result.tokens_used,
                    "model_output": result.model_output,
                    "agent_feedback": result.agent_feedback,
                    "error": result.error_message
                })
            
            # Format metrics
            formatted_metrics = []
            for metric in metrics:
                formatted_metrics.append({
                    "model_name": metric.model.name if metric.model else "Unknown",
                    "category": metric.category,
                    "avg_accuracy": metric.avg_accuracy,
                    "avg_response_time": metric.avg_response_time,
                    "total_cost": metric.total_cost,
                    "success_rate": metric.success_rate,
                    "accuracy_rank": metric.accuracy_rank,
                    "speed_rank": metric.speed_rank,
                    "cost_rank": metric.cost_rank,
                    "overall_rank": metric.overall_rank
                })
            
            return {
                "evaluation_run": {
                    "id": eval_run.id,
                    "name": eval_run.name,
                    "description": eval_run.description,
                    "status": eval_run.status,
                    "created_at": eval_run.created_at.isoformat()
                },
                "results": formatted_results,
                "metrics": formatted_metrics,
                "summary": {
                    "total_results": len(results),
                    "successful_results": len([r for r in results if not r.error_message]),
                    "categories": list(set(r.test_case.category for r in results)),
                    "models": list(set(r.model.name for r in results))
                }
            }
            
        finally:
            db.close() 