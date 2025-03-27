"""
Integrated Agent Framework for Code and Research Tasks

This module provides a robust, fault-tolerant framework that integrates coding agents
and research/planning agents using LangGraph for orchestration and reflection capabilities.
It builds upon the existing Potpie agent architecture while adding advanced planning and
self-improvement capabilities.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, TypedDict, Union, Literal
from pydantic import BaseModel, Field

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.modules.intelligence.agents.chat_agent import ChatAgent, ChatAgentResponse, ChatContext, ToolCallResponse


class AgentType(Enum):
    """Types of agents supported by the integrated framework."""
    CODE = "code"
    RESEARCH = "research"
    PLANNING = "planning"
    REFLECTION = "reflection"


class AgentState(TypedDict):
    """State object for tracking agent execution."""
    query: str
    context: Dict[str, Any]
    results: List[Dict[str, Any]]
    errors: Optional[List[str]]
    remaining_steps: int
    current_agent: str
    history: List[Dict[str, Any]]


class IntegratedAgentConfig(BaseModel):
    """Configuration for the integrated agent framework."""
    max_iterations: int = Field(default=5, description="Maximum number of iterations for the agent")
    agent_types: List[AgentType] = Field(default_factory=lambda: [AgentType.CODE], 
                                        description="Types of agents to include in the framework")
    reflection_enabled: bool = Field(default=True, description="Whether to enable reflection capabilities")
    fault_tolerance_level: int = Field(default=2, description="Level of fault tolerance (0-3)")
    tools: List[str] = Field(default_factory=list, description="List of tools to make available to agents")


class BaseIntegratedAgent(ChatAgent):
    """Base class for integrated agents that combines coding and research capabilities."""
    
    def __init__(self, config: IntegratedAgentConfig = None):
        """Initialize the integrated agent with the given configuration."""
        self.config = config or IntegratedAgentConfig()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the workflow graph for the agent."""
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent type
        if AgentType.CODE in self.config.agent_types:
            workflow.add_node("code_agent", self._code_agent_node)
        
        if AgentType.RESEARCH in self.config.agent_types:
            workflow.add_node("research_agent", self._research_agent_node)
        
        if AgentType.PLANNING in self.config.agent_types:
            workflow.add_node("planning_agent", self._planning_agent_node)
        
        # Add reflection node if enabled
        if self.config.reflection_enabled:
            workflow.add_node("reflection_agent", self._reflection_agent_node)
        
        # Set up the entry point based on configuration
        if AgentType.PLANNING in self.config.agent_types:
            workflow.set_entry_point("planning_agent")
        elif AgentType.RESEARCH in self.config.agent_types:
            workflow.set_entry_point("research_agent")
        else:
            workflow.set_entry_point("code_agent")
        
        # Add edges between nodes
        self._add_workflow_edges(workflow)
        
        return workflow.compile()
    
    def _add_workflow_edges(self, workflow: StateGraph) -> None:
        """Add edges between nodes in the workflow graph."""
        # Basic linear flow
        if AgentType.PLANNING in self.config.agent_types and AgentType.RESEARCH in self.config.agent_types:
            workflow.add_edge("planning_agent", "research_agent")
        
        if AgentType.RESEARCH in self.config.agent_types and AgentType.CODE in self.config.agent_types:
            workflow.add_edge("research_agent", "code_agent")
        
        # Add reflection edges if enabled
        if self.config.reflection_enabled:
            if AgentType.CODE in self.config.agent_types:
                workflow.add_edge("code_agent", "reflection_agent")
            
            # Add conditional edge from reflection back to appropriate agent
            workflow.add_conditional_edges(
                "reflection_agent",
                self._reflection_router,
                {
                    "end": END,
                    "code": "code_agent" if AgentType.CODE in self.config.agent_types else END,
                    "research": "research_agent" if AgentType.RESEARCH in self.config.agent_types else END,
                    "planning": "planning_agent" if AgentType.PLANNING in self.config.agent_types else END,
                },
            )
        else:
            # If reflection is disabled, end after code agent
            if AgentType.CODE in self.config.agent_types:
                workflow.add_edge("code_agent", END)
            elif AgentType.RESEARCH in self.config.agent_types:
                workflow.add_edge("research_agent", END)
    
    def _reflection_router(self, state: AgentState) -> Literal["end", "code", "research", "planning"]:
        """Route to the next agent based on reflection results."""
        # End if we've reached the maximum number of iterations
        if state["remaining_steps"] <= 0:
            return "end"
        
        # Check if there are errors that need to be addressed
        if state.get("errors") and len(state["errors"]) > 0:
            # Route to the appropriate agent based on the error type
            error_type = self._classify_error(state["errors"][-1])
            if error_type == "code" and AgentType.CODE in self.config.agent_types:
                return "code"
            elif error_type == "research" and AgentType.RESEARCH in self.config.agent_types:
                return "research"
            elif error_type == "planning" and AgentType.PLANNING in self.config.agent_types:
                return "planning"
        
        # If no errors or can't handle errors, end the workflow
        return "end"
    
    def _classify_error(self, error: str) -> str:
        """Classify the type of error to determine which agent should handle it."""
        # Simple classification based on keywords
        if any(kw in error.lower() for kw in ["code", "syntax", "runtime", "exception"]):
            return "code"
        elif any(kw in error.lower() for kw in ["research", "information", "data"]):
            return "research"
        elif any(kw in error.lower() for kw in ["plan", "strategy", "approach"]):
            return "planning"
        
        # Default to code errors if can't classify
        return "code"
    
    @abstractmethod
    def _code_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Process the state with the code agent."""
        pass
    
    @abstractmethod
    def _research_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Process the state with the research agent."""
        pass
    
    @abstractmethod
    def _planning_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Process the state with the planning agent."""
        pass
    
    @abstractmethod
    def _reflection_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Process the state with the reflection agent."""
        pass
    
    async def run(self, ctx: ChatContext) -> ChatAgentResponse:
        """Run the integrated agent workflow synchronously."""
        # Initialize the state
        state = {
            "query": ctx.query,
            "context": {
                "project_id": ctx.project_id,
                "agent_id": ctx.curr_agent_id,
                "history": ctx.history,
                "node_ids": ctx.node_ids or [],
                "additional_context": ctx.additional_context
            },
            "results": [],
            "errors": [],
            "remaining_steps": self.config.max_iterations,
            "current_agent": "",
            "history": []
        }
        
        # Run the workflow
        result = self.workflow.invoke(state)
        
        # Convert the result to a ChatAgentResponse
        return ChatAgentResponse(
            response=self._format_response(result),
            tool_calls=self._extract_tool_calls(result),
            citations=self._extract_citations(result)
        )
    
    async def run_stream(self, ctx: ChatContext) -> AsyncGenerator[ChatAgentResponse, None]:
        """Run the integrated agent workflow asynchronously, yielding partial results."""
        # Initialize the state
        state = {
            "query": ctx.query,
            "context": {
                "project_id": ctx.project_id,
                "agent_id": ctx.curr_agent_id,
                "history": ctx.history,
                "node_ids": ctx.node_ids or [],
                "additional_context": ctx.additional_context
            },
            "results": [],
            "errors": [],
            "remaining_steps": self.config.max_iterations,
            "current_agent": "",
            "history": []
        }
        
        # Stream the workflow execution
        async for event in self.workflow.astream(state):
            # Convert the intermediate result to a ChatAgentResponse
            yield ChatAgentResponse(
                response=self._format_response(event),
                tool_calls=self._extract_tool_calls(event),
                citations=self._extract_citations(event)
            )
    
    def _format_response(self, result: Dict[str, Any]) -> str:
        """Format the workflow result into a response string."""
        if not result.get("results"):
            return "No results were produced by the agent."
        
        # Combine all results into a single response
        response_parts = []
        for r in result["results"]:
            if r.get("content"):
                response_parts.append(r["content"])
        
        return "\n\n".join(response_parts)
    
    def _extract_tool_calls(self, result: Dict[str, Any]) -> List[ToolCallResponse]:
        """Extract tool calls from the workflow result."""
        tool_calls = []
        
        # Extract tool calls from the history
        for event in result.get("history", []):
            if event.get("tool_calls"):
                for tc in event["tool_calls"]:
                    tool_calls.append(ToolCallResponse(
                        call_id=tc.get("id", "unknown"),
                        event_type=tc.get("event_type", "call"),
                        tool_name=tc.get("name", "unknown"),
                        tool_response=tc.get("response", ""),
                        tool_call_details=tc.get("details", {})
                    ))
        
        return tool_calls
    
    def _extract_citations(self, result: Dict[str, Any]) -> List[str]:
        """Extract citations from the workflow result."""
        citations = []
        
        # Extract citations from the results
        for r in result.get("results", []):
            if r.get("citations"):
                citations.extend(r["citations"])
        
        return list(set(citations))  # Remove duplicates


class DefaultIntegratedAgent(BaseIntegratedAgent):
    """Default implementation of the integrated agent framework."""
    
    def _code_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Process the state with the code agent."""
        state["current_agent"] = "code_agent"
        
        try:
            # Implement code agent logic here
            # This is a placeholder implementation
            result = {
                "content": f"Code agent processed query: {state['query']}",
                "citations": []
            }
            
            # Update the state
            state["results"].append(result)
            state["history"].append({
                "agent": "code_agent",
                "result": result,
                "tool_calls": []
            })
            state["remaining_steps"] -= 1
            
            return state
        except Exception as e:
            # Handle errors with fault tolerance
            error_msg = f"Error in code agent: {str(e)}"
            state["errors"] = state.get("errors", []) + [error_msg]
            
            # If fault tolerance is high enough, try to recover
            if self.config.fault_tolerance_level >= 2:
                result = {
                    "content": "The code agent encountered an error but is attempting to recover.",
                    "citations": []
                }
                state["results"].append(result)
            
            return state
    
    def _research_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Process the state with the research agent."""
        state["current_agent"] = "research_agent"
        
        try:
            # Implement research agent logic here
            # This is a placeholder implementation
            result = {
                "content": f"Research agent processed query: {state['query']}",
                "citations": ["research_source_1", "research_source_2"]
            }
            
            # Update the state
            state["results"].append(result)
            state["history"].append({
                "agent": "research_agent",
                "result": result,
                "tool_calls": []
            })
            state["remaining_steps"] -= 1
            
            return state
        except Exception as e:
            # Handle errors with fault tolerance
            error_msg = f"Error in research agent: {str(e)}"
            state["errors"] = state.get("errors", []) + [error_msg]
            
            # If fault tolerance is high enough, try to recover
            if self.config.fault_tolerance_level >= 2:
                result = {
                    "content": "The research agent encountered an error but is attempting to recover.",
                    "citations": []
                }
                state["results"].append(result)
            
            return state
    
    def _planning_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Process the state with the planning agent."""
        state["current_agent"] = "planning_agent"
        
        try:
            # Implement planning agent logic here
            # This is a placeholder implementation
            result = {
                "content": f"Planning agent processed query: {state['query']}",
                "citations": []
            }
            
            # Update the state
            state["results"].append(result)
            state["history"].append({
                "agent": "planning_agent",
                "result": result,
                "tool_calls": []
            })
            state["remaining_steps"] -= 1
            
            return state
        except Exception as e:
            # Handle errors with fault tolerance
            error_msg = f"Error in planning agent: {str(e)}"
            state["errors"] = state.get("errors", []) + [error_msg]
            
            # If fault tolerance is high enough, try to recover
            if self.config.fault_tolerance_level >= 2:
                result = {
                    "content": "The planning agent encountered an error but is attempting to recover.",
                    "citations": []
                }
                state["results"].append(result)
            
            return state
    
    def _reflection_agent_node(self, state: AgentState) -> Dict[str, Any]:
        """Process the state with the reflection agent."""
        state["current_agent"] = "reflection_agent"
        
        try:
            # Implement reflection agent logic here
            # This is a placeholder implementation
            
            # Check if there are any errors to address
            if state.get("errors") and len(state["errors"]) > 0:
                result = {
                    "content": f"Reflection agent identified issues: {state['errors'][-1]}",
                    "citations": []
                }
            else:
                # Check the quality of the results
                result = {
                    "content": "Reflection agent reviewed the results and found them satisfactory.",
                    "citations": []
                }
            
            # Update the state
            state["results"].append(result)
            state["history"].append({
                "agent": "reflection_agent",
                "result": result,
                "tool_calls": []
            })
            state["remaining_steps"] -= 1
            
            return state
        except Exception as e:
            # Handle errors with fault tolerance
            error_msg = f"Error in reflection agent: {str(e)}"
            state["errors"] = state.get("errors", []) + [error_msg]
            
            # Even if reflection fails, we should continue with the workflow
            return state