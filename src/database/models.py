from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class EvaluationRun(Base):
    """Represents a complete evaluation run across multiple models"""
    __tablename__ = "evaluation_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="running")  # running, completed, failed
    
    # Relationships
    results = relationship("EvaluationResult", back_populates="evaluation_run")

class LLMModel(Base):
    """Represents an LLM model configuration"""
    __tablename__ = "llm_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    provider = Column(String, nullable=False)  # openai, anthropic, local
    model_id = Column(String, nullable=False)  # gpt-4, claude-3-sonnet, etc.
    api_endpoint = Column(String)
    cost_per_1k_tokens = Column(Float, default=0.0)
    max_tokens = Column(Integer, default=4096)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    results = relationship("EvaluationResult", back_populates="model")
    performance_metrics = relationship("PerformanceMetrics", back_populates="model")

class TestCase(Base):
    """Represents individual test cases"""
    __tablename__ = "test_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # summarization, qa, reasoning
    input_text = Column(Text, nullable=False)
    expected_output = Column(Text)
    evaluation_criteria = Column(Text)
    difficulty_level = Column(String, default="medium")  # easy, medium, hard
    
    # Relationships
    results = relationship("EvaluationResult", back_populates="test_case")

class EvaluationResult(Base):
    """Stores results of individual test case evaluations"""
    __tablename__ = "evaluation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    evaluation_run_id = Column(Integer, ForeignKey("evaluation_runs.id"))
    model_id = Column(Integer, ForeignKey("llm_models.id"))
    test_case_id = Column(Integer, ForeignKey("test_cases.id"))
    
    # Result data
    model_output = Column(Text)
    accuracy_score = Column(Float)
    response_time_ms = Column(Float)
    tokens_used = Column(Integer)
    cost_usd = Column(Float)
    error_message = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    agent_feedback = Column(Text)  # Feedback from evaluator agents
    
    # Relationships
    evaluation_run = relationship("EvaluationRun", back_populates="results")
    model = relationship("LLMModel", back_populates="results")
    test_case = relationship("TestCase", back_populates="results")

class PerformanceMetrics(Base):
    """Aggregated performance metrics for model comparisons"""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    evaluation_run_id = Column(Integer, ForeignKey("evaluation_runs.id"))
    model_id = Column(Integer, ForeignKey("llm_models.id"))
    category = Column(String)  # summarization, qa, reasoning, overall
    
    # Aggregated metrics
    avg_accuracy = Column(Float)
    avg_response_time = Column(Float)
    total_cost = Column(Float)
    total_tokens = Column(Integer)
    success_rate = Column(Float)
    
    # Rankings
    accuracy_rank = Column(Integer)
    speed_rank = Column(Integer)
    cost_rank = Column(Integer)
    overall_rank = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    evaluation_run = relationship("EvaluationRun")
    model = relationship("LLMModel", back_populates="performance_metrics") 