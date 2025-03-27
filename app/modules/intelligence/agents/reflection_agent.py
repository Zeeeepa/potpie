"""
Reflection Agent Implementation

This module provides a specialized reflection agent that can be used independently
or as part of the integrated agent framework. It evaluates the output of other agents
and provides feedback for improvement.
"""

from typing import Any, AsyncGenerator, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from app.modules.intelligence.agents.chat_agent import ChatAgent, ChatAgentResponse, ChatContext, ToolCallResponse


class ReflectionFeedback(BaseModel):
    """Feedback from the reflection agent."""
    quality_score: float = Field(..., description="Overall quality score (0-1)")
    strengths: List[str] = Field(default_factory=list, description="Strengths of the output")
    weaknesses: List[str] = Field(default_factory=list, description="Weaknesses of the output")
    improvement_suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    needs_revision: bool = Field(..., description="Whether the output needs revision")


class ReflectionAgentConfig(BaseModel):
    """Configuration for the reflection agent."""
    quality_threshold: float = Field(default=0.8, description="Threshold for acceptable quality (0-1)")
    evaluation_criteria: List[str] = Field(
        default_factory=lambda: ["accuracy", "completeness", "clarity", "relevance"],
        description="Criteria to evaluate"
    )
    detailed_feedback: bool = Field(default=True, description="Whether to provide detailed feedback")


class ReflectionAgent(ChatAgent):
    """Agent specialized in reflection and evaluation."""
    
    def __init__(self, config: ReflectionAgentConfig = None):
        """Initialize the reflection agent with the given configuration."""
        self.config = config or ReflectionAgentConfig()
    
    async def run(self, ctx: ChatContext) -> ChatAgentResponse:
        """Run the reflection agent synchronously."""
        # Extract the content to reflect on from the history
        content_to_reflect = self._extract_content_to_reflect(ctx.history)
        
        # Evaluate the content
        feedback = self._evaluate_content(content_to_reflect, ctx.query)
        
        # Format the feedback as a response
        response = self._format_feedback(feedback)
        
        return ChatAgentResponse(
            response=response,
            tool_calls=[],  # No tool calls in this simple implementation
            citations=[]  # No citations in this simple implementation
        )
    
    async def run_stream(self, ctx: ChatContext) -> AsyncGenerator[ChatAgentResponse, None]:
        """Run the reflection agent asynchronously, yielding partial results."""
        # This is a simplified implementation that doesn't actually stream
        # In a real implementation, you would yield partial results as they become available
        content_to_reflect = self._extract_content_to_reflect(ctx.history)
        feedback = self._evaluate_content(content_to_reflect, ctx.query)
        response = self._format_feedback(feedback)
        
        yield ChatAgentResponse(
            response=response,
            tool_calls=[],
            citations=[]
        )
    
    def _extract_content_to_reflect(self, history: List[str]) -> str:
        """Extract the content to reflect on from the history."""
        # This is a simplified implementation
        # In a real implementation, you would extract the most recent non-reflection message
        if not history:
            return "No content to reflect on."
        
        # Just use the last message in history for simplicity
        return history[-1]
    
    def _evaluate_content(self, content: str, query: str) -> ReflectionFeedback:
        """Evaluate the content based on the configured criteria."""
        # This is a placeholder implementation
        # In a real implementation, you would use an LLM to evaluate the content
        
        # Simulate evaluation based on simple heuristics
        strengths = []
        weaknesses = []
        improvement_suggestions = []
        
        # Check for accuracy (placeholder logic)
        if "error" in content.lower() or "incorrect" in content.lower():
            weaknesses.append("The content contains errors or incorrect information.")
            improvement_suggestions.append("Verify facts and correct any errors.")
        else:
            strengths.append("The content appears to be accurate.")
        
        # Check for completeness (placeholder logic)
        if len(content) < 100:
            weaknesses.append("The content is too brief and may not be complete.")
            improvement_suggestions.append("Expand the content to cover more aspects of the query.")
        else:
            strengths.append("The content is sufficiently detailed.")
        
        # Check for clarity (placeholder logic)
        if "unclear" in content.lower() or "confusing" in content.lower():
            weaknesses.append("Some parts of the content may be unclear or confusing.")
            improvement_suggestions.append("Clarify ambiguous statements and use simpler language.")
        else:
            strengths.append("The content is clear and easy to understand.")
        
        # Check for relevance (placeholder logic)
        if query.lower() not in content.lower():
            weaknesses.append("The content may not directly address the query.")
            improvement_suggestions.append("Ensure the content directly addresses the original query.")
        else:
            strengths.append("The content is relevant to the query.")
        
        # Calculate quality score based on strengths and weaknesses
        quality_score = 0.5 + (len(strengths) * 0.1) - (len(weaknesses) * 0.1)
        quality_score = max(0.0, min(1.0, quality_score))  # Clamp between 0 and 1
        
        # Determine if revision is needed
        needs_revision = quality_score < self.config.quality_threshold
        
        return ReflectionFeedback(
            quality_score=quality_score,
            strengths=strengths,
            weaknesses=weaknesses,
            improvement_suggestions=improvement_suggestions,
            needs_revision=needs_revision
        )
    
    def _format_feedback(self, feedback: ReflectionFeedback) -> str:
        """Format the feedback as a response string."""
        parts = [
            f"# Reflection Feedback",
            f"\n## Quality Score: {feedback.quality_score:.2f}/1.00",
            f"\n**Needs Revision**: {'Yes' if feedback.needs_revision else 'No'}"
        ]
        
        if self.config.detailed_feedback:
            if feedback.strengths:
                parts.append("\n## Strengths")
                for strength in feedback.strengths:
                    parts.append(f"- {strength}")
            
            if feedback.weaknesses:
                parts.append("\n## Areas for Improvement")
                for weakness in feedback.weaknesses:
                    parts.append(f"- {weakness}")
            
            if feedback.improvement_suggestions:
                parts.append("\n## Suggestions")
                for suggestion in feedback.improvement_suggestions:
                    parts.append(f"- {suggestion}")
        
        if feedback.needs_revision:
            parts.append("\n## Next Steps")
            parts.append("Please revise the content based on the feedback above.")
        else:
            parts.append("\n## Conclusion")
            parts.append("The content meets the quality threshold and is ready for use.")
        
        return "\n".join(parts)