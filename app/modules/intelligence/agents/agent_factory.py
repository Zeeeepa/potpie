"""
Agent Factory Module

This module provides a factory for creating different types of agents based on configuration.
It serves as the main entry point for creating and configuring agents in the integrated framework.
"""

from typing import Dict, List, Optional, Type, Union

from app.modules.intelligence.agents.chat_agent import ChatAgent, AgentWithInfo
from app.modules.intelligence.agents.integrated_agent_framework import (
    AgentType, BaseIntegratedAgent, DefaultIntegratedAgent, IntegratedAgentConfig
)
from app.modules.intelligence.agents.research_agent import ResearchAgent, ResearchAgentConfig
from app.modules.intelligence.agents.planning_agent import PlanningAgent, PlanningAgentConfig
from app.modules.intelligence.agents.reflection_agent import ReflectionAgent, ReflectionAgentConfig


class AgentFactory:
    """Factory for creating different types of agents."""
    
    @staticmethod
    def create_agent(
        agent_type: str,
        config: Optional[Dict] = None,
        agent_id: str = "custom_agent",
        agent_name: str = "Custom Agent",
        agent_description: str = "A custom agent"
    ) -> AgentWithInfo:
        """Create an agent of the specified type with the given configuration.
        
        Args:
            agent_type: Type of agent to create
            config: Configuration for the agent
            agent_id: ID for the agent
            agent_name: Name for the agent
            agent_description: Description of the agent
            
        Returns:
            An AgentWithInfo object containing the agent and its metadata
        """
        config = config or {}
        
        if agent_type == "integrated":
            # Convert agent_types from strings to enum values
            if "agent_types" in config:
                config["agent_types"] = [
                    AgentType(at) if isinstance(at, str) else at
                    for at in config["agent_types"]
                ]
            
            agent_config = IntegratedAgentConfig(**config)
            agent = DefaultIntegratedAgent(config=agent_config)
            
        elif agent_type == "research":
            agent_config = ResearchAgentConfig(**config)
            agent = ResearchAgent(config=agent_config)
            
        elif agent_type == "planning":
            agent_config = PlanningAgentConfig(**config)
            agent = PlanningAgent(config=agent_config)
            
        elif agent_type == "reflection":
            agent_config = ReflectionAgentConfig(**config)
            agent = ReflectionAgent(config=agent_config)
            
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        return AgentWithInfo(
            agent=agent,
            id=agent_id,
            name=agent_name,
            description=agent_description
        )
    
    @staticmethod
    def create_integrated_agent(
        agent_types: List[Union[str, AgentType]] = None,
        max_iterations: int = 5,
        reflection_enabled: bool = True,
        fault_tolerance_level: int = 2,
        tools: List[str] = None,
        agent_id: str = "integrated_agent",
        agent_name: str = "Integrated Agent",
        agent_description: str = "An agent that combines multiple specialized agents"
    ) -> AgentWithInfo:
        """Create an integrated agent with the specified configuration.
        
        Args:
            agent_types: Types of agents to include
            max_iterations: Maximum number of iterations
            reflection_enabled: Whether to enable reflection
            fault_tolerance_level: Level of fault tolerance
            tools: Tools to make available to the agent
            agent_id: ID for the agent
            agent_name: Name for the agent
            agent_description: Description of the agent
            
        Returns:
            An AgentWithInfo object containing the integrated agent and its metadata
        """
        # Convert agent_types from strings to enum values if needed
        if agent_types:
            agent_types = [
                AgentType(at) if isinstance(at, str) else at
                for at in agent_types
            ]
        
        config = IntegratedAgentConfig(
            agent_types=agent_types or [AgentType.CODE],
            max_iterations=max_iterations,
            reflection_enabled=reflection_enabled,
            fault_tolerance_level=fault_tolerance_level,
            tools=tools or []
        )
        
        agent = DefaultIntegratedAgent(config=config)
        
        return AgentWithInfo(
            agent=agent,
            id=agent_id,
            name=agent_name,
            description=agent_description
        )
    
    @staticmethod
    def create_research_agent(
        max_sources: int = 5,
        min_relevance_score: float = 0.7,
        search_depth: int = 2,
        include_web_search: bool = True,
        include_code_search: bool = True,
        include_documentation: bool = True,
        agent_id: str = "research_agent",
        agent_name: str = "Research Agent",
        agent_description: str = "An agent specialized in research tasks"
    ) -> AgentWithInfo:
        """Create a research agent with the specified configuration."""
        config = ResearchAgentConfig(
            max_sources=max_sources,
            min_relevance_score=min_relevance_score,
            search_depth=search_depth,
            include_web_search=include_web_search,
            include_code_search=include_code_search,
            include_documentation=include_documentation
        )
        
        agent = ResearchAgent(config=config)
        
        return AgentWithInfo(
            agent=agent,
            id=agent_id,
            name=agent_name,
            description=agent_description
        )
    
    @staticmethod
    def create_planning_agent(
        max_steps: int = 10,
        detail_level: str = "medium",
        include_constraints: bool = True,
        include_assumptions: bool = True,
        agent_id: str = "planning_agent",
        agent_name: str = "Planning Agent",
        agent_description: str = "An agent specialized in planning tasks"
    ) -> AgentWithInfo:
        """Create a planning agent with the specified configuration."""
        config = PlanningAgentConfig(
            max_steps=max_steps,
            detail_level=detail_level,
            include_constraints=include_constraints,
            include_assumptions=include_assumptions
        )
        
        agent = PlanningAgent(config=config)
        
        return AgentWithInfo(
            agent=agent,
            id=agent_id,
            name=agent_name,
            description=agent_description
        )
    
    @staticmethod
    def create_reflection_agent(
        quality_threshold: float = 0.8,
        evaluation_criteria: List[str] = None,
        detailed_feedback: bool = True,
        agent_id: str = "reflection_agent",
        agent_name: str = "Reflection Agent",
        agent_description: str = "An agent specialized in reflection and evaluation"
    ) -> AgentWithInfo:
        """Create a reflection agent with the specified configuration."""
        config = ReflectionAgentConfig(
            quality_threshold=quality_threshold,
            evaluation_criteria=evaluation_criteria or ["accuracy", "completeness", "clarity", "relevance"],
            detailed_feedback=detailed_feedback
        )
        
        agent = ReflectionAgent(config=config)
        
        return AgentWithInfo(
            agent=agent,
            id=agent_id,
            name=agent_name,
            description=agent_description
        )