from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from .models import Base
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./llm_evaluation.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    echo=True  # Set to False in production
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with sample data"""
    create_tables()
    
    db = SessionLocal()
    try:
        # Check if we already have data
        from .models import LLMModel, TestCase
        
        if db.query(LLMModel).count() == 0:
            # Add sample LLM models
            models = [
                LLMModel(
                    name="GPT-4",
                    provider="openai",
                    model_id="gpt-4",
                    cost_per_1k_tokens=0.03,
                    max_tokens=8192
                ),
                LLMModel(
                    name="GPT-3.5 Turbo",
                    provider="openai", 
                    model_id="gpt-3.5-turbo",
                    cost_per_1k_tokens=0.002,
                    max_tokens=4096
                ),
                LLMModel(
                    name="Claude 3 Sonnet",
                    provider="anthropic",
                    model_id="claude-3-sonnet-20240229",
                    cost_per_1k_tokens=0.015,
                    max_tokens=4096
                ),
                LLMModel(
                    name="Mock Model",
                    provider="mock",
                    model_id="mock-model",
                    cost_per_1k_tokens=0.001,
                    max_tokens=2048
                )
            ]
            db.add_all(models)
        
        if db.query(TestCase).count() == 0:
            # Add sample test cases
            test_cases = [
                # Summarization tests
                TestCase(
                    name="News Article Summary",
                    category="summarization",
                    input_text="""The global technology sector experienced significant volatility in 2023, with artificial intelligence companies seeing unprecedented growth while traditional software companies faced headwinds. Major tech giants like Microsoft, Google, and OpenAI made substantial investments in AI infrastructure, leading to a new wave of innovation but also raising concerns about market concentration. Meanwhile, regulatory bodies worldwide began implementing stricter guidelines for AI development and deployment, particularly focusing on data privacy and algorithmic bias. The semiconductor industry, crucial for AI development, faced supply chain challenges but also benefited from increased demand for specialized AI chips.""",
                    expected_output="Tech sector showed mixed results in 2023: AI companies grew rapidly with major investments from Microsoft, Google, and OpenAI, while traditional software struggled. New regulations emerged focusing on AI privacy and bias, and semiconductor industry faced supply challenges despite increased AI chip demand.",
                    evaluation_criteria="Accuracy, conciseness, key point coverage",
                    difficulty_level="medium"
                ),
                
                # Q&A tests
                TestCase(
                    name="Factual Question",
                    category="qa",
                    input_text="What is the capital of Australia and what is its population approximately?",
                    expected_output="The capital of Australia is Canberra, with a population of approximately 430,000-450,000 people.",
                    evaluation_criteria="Factual accuracy, completeness",
                    difficulty_level="easy"
                ),
                
                # Reasoning tests
                TestCase(
                    name="Logic Puzzle",
                    category="reasoning",
                    input_text="If all roses are flowers, and all flowers need water, and some roses are red, can we conclude that some red things need water?",
                    expected_output="Yes, we can conclude that some red things need water. Since some roses are red, and all roses are flowers, those red roses are flowers. Since all flowers need water, those red roses (which are red things) need water.",
                    evaluation_criteria="Logical reasoning, step-by-step explanation",
                    difficulty_level="medium"
                ),
                
                # Additional test cases
                TestCase(
                    name="Complex Summarization",
                    category="summarization", 
                    input_text="""Climate change research published in 2023 revealed accelerating trends in global temperature rise, with the past decade marking the warmest on record. Scientists from over 50 countries collaborated on comprehensive studies showing that carbon dioxide levels have reached 421 ppm, the highest in human history. The research highlighted regional variations, with Arctic regions warming twice as fast as the global average, leading to accelerated ice sheet melting and sea level rise. Economic impacts were quantified at $23 trillion globally by 2050 if current trends continue. However, the studies also identified promising developments in renewable energy adoption, with solar and wind power costs declining by 60% since 2020. Policy recommendations included immediate implementation of carbon pricing mechanisms and increased investment in climate adaptation infrastructure.""",
                    expected_output="2023 climate research shows record warming with CO2 at historic high of 421 ppm. Arctic warming twice the global rate, causing ice melt and sea rise. Economic damage projected at $23 trillion by 2050, but renewable energy costs dropped 60% since 2020. Scientists recommend carbon pricing and adaptation infrastructure investment.",
                    evaluation_criteria="Accuracy, completeness, conciseness",
                    difficulty_level="hard"
                ),
                
                TestCase(
                    name="Mathematical Reasoning",
                    category="reasoning",
                    input_text="A company's revenue increased by 25% in the first quarter, then decreased by 20% in the second quarter. If the revenue at the end of the second quarter was $300,000, what was the original revenue at the start of the first quarter?",
                    expected_output="Let's work backwards. If Q2 revenue is $300,000 after a 20% decrease, then Q1 revenue was $300,000 ÷ 0.8 = $375,000. If Q1 revenue of $375,000 represents a 25% increase from the original, then the original revenue was $375,000 ÷ 1.25 = $300,000.",
                    evaluation_criteria="Mathematical accuracy, step-by-step reasoning",
                    difficulty_level="medium"
                )
            ]
            db.add_all(test_cases)
        
        db.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close() 