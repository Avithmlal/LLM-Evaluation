import autogen
from typing import Dict, Any, List
import asyncio
import re

class EvaluatorAgent:
    """Base class for evaluator agents"""
    
    def __init__(self, name: str, system_message: str):
        self.name = name
        self.system_message = system_message
        self.agent = autogen.AssistantAgent(
            name=name,
            system_message=system_message,
            llm_config={"config_list": [{"model": "gpt-4", "api_key": "dummy"}]}
        )
    
    async def evaluate_response(self, test_case: Dict[str, Any], model_response: str) -> Dict[str, Any]:
        """Evaluate model response against test case"""
        raise NotImplementedError("Subclasses must implement evaluate_response")
    
    def _extract_score(self, evaluation_text: str) -> float:
        """Extract numerical score from evaluation text"""
        # Look for patterns like "Score: 8.5" or "Rating: 7/10"
        patterns = [
            r"score[:\s]+([0-9.]+)",
            r"rating[:\s]+([0-9.]+)",
            r"([0-9.]+)\s*/\s*10",
            r"([0-9.]+)\s*/\s*100"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, evaluation_text.lower())
            if match:
                score = float(match.group(1))
                # Normalize to 0-1 scale
                if "/10" in evaluation_text.lower():
                    return score / 10
                elif "/100" in evaluation_text.lower():
                    return score / 100
                elif score <= 1:
                    return score
                elif score <= 10:
                    return score / 10
                else:
                    return score / 100
        
        # Default scoring based on keywords if no numerical score found
        positive_keywords = ["good", "excellent", "accurate", "correct", "comprehensive"]
        negative_keywords = ["poor", "incorrect", "inaccurate", "incomplete", "wrong"]
        
        text_lower = evaluation_text.lower()
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        if positive_count > negative_count:
            return 0.75
        elif negative_count > positive_count:
            return 0.35
        else:
            return 0.55  # Neutral

class SummarizationEvaluator(EvaluatorAgent):
    """Agent for evaluating summarization tasks"""
    
    def __init__(self):
        system_message = """
        You are a summarization evaluation expert. Your task is to evaluate how well a model summarizes given text.
        
        Evaluation criteria:
        1. Accuracy: Does the summary capture the key points correctly?
        2. Completeness: Are all important points included?
        3. Conciseness: Is the summary appropriately condensed?
        4. Clarity: Is the summary clear and well-structured?
        5. Faithfulness: Does it stay true to the original content?
        
        For each evaluation, provide:
        - A score from 0 to 10 (where 10 is perfect)
        - Specific feedback on strengths and weaknesses
        - Comparison with the expected output if provided
        
        Format your response as:
        Score: [0-10]
        Feedback: [Detailed feedback]
        """
        super().__init__("SummarizationEvaluator", system_message)
    
    async def evaluate_response(self, test_case: Dict[str, Any], model_response: str) -> Dict[str, Any]:
        """Evaluate summarization response"""
        prompt = f"""
        Original Text:
        {test_case['input_text']}
        
        Model Summary:
        {model_response}
        
        Expected Summary (reference):
        {test_case.get('expected_output', 'Not provided')}
        
        Please evaluate this summary based on the criteria mentioned in your system message.
        """
        
        # Mock evaluation for demo (in real implementation, this would use AutoGen)
        evaluation = self._mock_evaluation(test_case, model_response, "summarization")
        
        return {
            "score": self._extract_score(evaluation),
            "feedback": evaluation,
            "category": "summarization",
            "evaluator": self.name
        }
    
    def _mock_evaluation(self, test_case: Dict[str, Any], model_response: str, category: str) -> str:
        """Generate mock evaluation for demo purposes"""
        # Simple heuristic-based evaluation
        original_length = len(test_case['input_text'])
        summary_length = len(model_response)
        compression_ratio = summary_length / original_length
        
        # Check if summary is appropriately compressed
        if compression_ratio < 0.2:
            score = 8.5
            feedback = "Excellent compression ratio. The summary effectively condenses the original text while maintaining key information."
        elif compression_ratio < 0.4:
            score = 7.5
            feedback = "Good summarization with appropriate length reduction. Most key points are captured."
        else:
            score = 6.0
            feedback = "Summary could be more concise. Consider reducing length while preserving essential information."
        
        # Check for key terms from original
        original_words = set(test_case['input_text'].lower().split())
        summary_words = set(model_response.lower().split())
        overlap = len(original_words.intersection(summary_words)) / len(original_words)
        
        if overlap > 0.3:
            score += 1.0
            feedback += " Good preservation of key terminology."
        
        return f"Score: {min(score, 10.0):.1f}\nFeedback: {feedback}"

class QAEvaluator(EvaluatorAgent):
    """Agent for evaluating Q&A tasks"""
    
    def __init__(self):
        system_message = """
        You are a Q&A evaluation expert. Your task is to evaluate how well a model answers questions.
        
        Evaluation criteria:
        1. Accuracy: Is the answer factually correct?
        2. Completeness: Does it fully address the question?
        3. Relevance: Is the response on-topic?
        4. Clarity: Is the answer clear and understandable?
        5. Helpfulness: Does it provide useful information?
        
        For each evaluation, provide:
        - A score from 0 to 10 (where 10 is perfect)
        - Specific feedback on accuracy and completeness
        - Comparison with the expected answer if provided
        
        Format your response as:
        Score: [0-10]
        Feedback: [Detailed feedback]
        """
        super().__init__("QAEvaluator", system_message)
    
    async def evaluate_response(self, test_case: Dict[str, Any], model_response: str) -> Dict[str, Any]:
        """Evaluate Q&A response"""
        evaluation = self._mock_evaluation(test_case, model_response, "qa")
        
        return {
            "score": self._extract_score(evaluation),
            "feedback": evaluation,
            "category": "qa",
            "evaluator": self.name
        }
    
    def _mock_evaluation(self, test_case: Dict[str, Any], model_response: str, category: str) -> str:
        """Generate mock Q&A evaluation"""
        expected = test_case.get('expected_output', '').lower()
        response = model_response.lower()
        
        # Simple keyword matching
        if expected:
            expected_words = set(expected.split())
            response_words = set(response.split())
            overlap = len(expected_words.intersection(response_words)) / len(expected_words)
            
            if overlap > 0.7:
                score = 9.0
                feedback = "Excellent accuracy. The answer closely matches expected content with high keyword overlap."
            elif overlap > 0.5:
                score = 7.5
                feedback = "Good accuracy. Most key information is present with reasonable alignment to expected answer."
            else:
                score = 6.0
                feedback = "Moderate accuracy. Some expected information is missing or incorrectly stated."
        else:
            # General quality assessment
            if len(response) > 50 and "?" not in response:
                score = 7.0
                feedback = "Reasonable response length and structure. Answer appears complete and relevant."
            else:
                score = 5.0
                feedback = "Response may be too brief or unclear. Consider providing more detailed information."
        
        return f"Score: {score:.1f}\nFeedback: {feedback}"

class ReasoningEvaluator(EvaluatorAgent):
    """Agent for evaluating reasoning tasks"""
    
    def __init__(self):
        system_message = """
        You are a logical reasoning evaluation expert. Your task is to evaluate reasoning capabilities.
        
        Evaluation criteria:
        1. Logic: Is the reasoning logically sound?
        2. Structure: Is the argument well-structured?
        3. Completeness: Are all steps clearly explained?
        4. Validity: Are conclusions properly supported?
        5. Clarity: Is the reasoning easy to follow?
        
        For each evaluation, provide:
        - A score from 0 to 10 (where 10 is perfect)
        - Assessment of logical structure and validity
        - Identification of any reasoning errors
        
        Format your response as:
        Score: [0-10]
        Feedback: [Detailed feedback]
        """
        super().__init__("ReasoningEvaluator", system_message)
    
    async def evaluate_response(self, test_case: Dict[str, Any], model_response: str) -> Dict[str, Any]:
        """Evaluate reasoning response"""
        evaluation = self._mock_evaluation(test_case, model_response, "reasoning")
        
        return {
            "score": self._extract_score(evaluation),
            "feedback": evaluation,
            "category": "reasoning",
            "evaluator": self.name
        }
    
    def _mock_evaluation(self, test_case: Dict[str, Any], model_response: str, category: str) -> str:
        """Generate mock reasoning evaluation"""
        response = model_response.lower()
        
        # Check for structured reasoning indicators
        structure_indicators = ["step", "first", "second", "therefore", "because", "since", "conclusion"]
        structure_count = sum(1 for indicator in structure_indicators if indicator in response)
        
        # Check for logical connectives
        logical_words = ["if", "then", "and", "or", "not", "all", "some", "therefore"]
        logical_count = sum(1 for word in logical_words if word in response)
        
        score = 5.0  # Base score
        
        if structure_count >= 3:
            score += 2.0
            feedback = "Well-structured reasoning with clear step-by-step analysis."
        elif structure_count >= 1:
            score += 1.0
            feedback = "Some structure present in the reasoning process."
        else:
            feedback = "Reasoning could benefit from more structured approach."
        
        if logical_count >= 5:
            score += 2.0
            feedback += " Strong use of logical connectives and formal reasoning."
        elif logical_count >= 2:
            score += 1.0
            feedback += " Adequate use of logical language."
        
        if len(response) > 200:
            score += 1.0
            feedback += " Comprehensive explanation provided."
        
        return f"Score: {min(score, 10.0):.1f}\nFeedback: {feedback}"

class AnalystAgent(EvaluatorAgent):
    """Agent for analyzing and reporting evaluation results"""
    
    def __init__(self):
        system_message = """
        You are a data analyst specializing in LLM evaluation results. Your task is to:
        1. Analyze performance metrics across different models
        2. Identify patterns and trends in the data
        3. Generate comprehensive comparison reports
        4. Provide actionable insights and recommendations
        
        Focus on metrics like accuracy, speed, cost, and overall performance rankings.
        """
        super().__init__("AnalystAgent", system_message)
    
    async def generate_analysis_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        # This would contain actual analysis logic
        # For now, return a structured template
        
        return {
            "summary": "Analysis complete. Performance varies across models and test categories.",
            "recommendations": [
                "Consider cost-performance trade-offs when selecting models",
                "Different models excel in different categories",
                "Monitor response times for production deployment"
            ],
            "key_insights": [
                "Model A shows best accuracy for summarization tasks",
                "Model B provides fastest response times",
                "Model C offers best cost efficiency"
            ]
        } 