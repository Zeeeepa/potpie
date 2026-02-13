# Integrated Agent Framework

This directory contains the implementation of an integrated agent framework that combines coding, research, and planning capabilities with reflection for continuous improvement.

## Overview

The integrated agent framework provides a robust, fault-tolerant system for automating complex software engineering tasks. It builds upon the existing Potpie agent architecture while adding advanced planning and self-improvement capabilities through LangGraph integration.

## Key Components

### 1. Agent Types

The framework supports several specialized agent types:

- **Code Agent**: Handles code generation, analysis, and modification tasks
- **Research Agent**: Gathers information from various sources to support decision-making
- **Planning Agent**: Creates structured plans for implementing features or solving problems
- **Reflection Agent**: Evaluates the output of other agents and provides feedback for improvement

### 2. Integration Architecture

The agents are integrated using a LangGraph-based workflow that allows them to work together seamlessly:

```
Planning Agent → Research Agent → Code Agent → Reflection Agent
                                                    ↑
                                                    |
                                                    ↓
                                 (feedback loop based on quality assessment)
```

### 3. Fault Tolerance

The framework includes built-in fault tolerance mechanisms:

- Error detection and classification
- Automatic routing to the appropriate agent for error resolution
- Configurable maximum iteration count to prevent infinite loops
- Graceful degradation when components fail

### 4. Agent Factory

The `AgentFactory` class provides a simple interface for creating and configuring agents:

```python
from app.modules.intelligence.agents.agent_factory import AgentFactory

# Create an integrated agent with all capabilities
agent = AgentFactory.create_integrated_agent(
    agent_types=["planning", "research", "code", "reflection"],
    max_iterations=5,
    reflection_enabled=True,
    fault_tolerance_level=2
)

# Create a specialized research agent
research_agent = AgentFactory.create_research_agent(
    max_sources=10,
    include_web_search=True,
    include_code_search=True
)
```

## Usage Examples

### Basic Usage

```python
from app.modules.intelligence.agents.agent_factory import AgentFactory

# Create an integrated agent
agent = AgentFactory.create_integrated_agent()

# Create a context for the agent
from app.modules.intelligence.agents.chat_agent import ChatContext
context = ChatContext(
    project_id="my_project",
    curr_agent_id="integrated_agent",
    history=[],
    query="Implement a fault-tolerant caching system"
)

# Run the agent
response = await agent.agent.run(context)
print(response.response)
```

### Customizing Agent Behavior

```python
from app.modules.intelligence.agents.agent_factory import AgentFactory
from app.modules.intelligence.agents.integrated_agent_framework import AgentType

# Create a planning-focused agent
planning_agent = AgentFactory.create_integrated_agent(
    agent_types=[AgentType.PLANNING, AgentType.REFLECTION],
    max_iterations=3,
    agent_id="planning_specialist",
    agent_name="Planning Specialist",
    agent_description="An agent specialized in creating detailed implementation plans"
)
```

## Extending the Framework

To add new agent types or capabilities:

1. Create a new agent class that implements the `ChatAgent` interface
2. Add the agent type to the `AgentType` enum in `integrated_agent_framework.py`
3. Update the `AgentFactory` class to support creating the new agent type
4. Modify the workflow edges in `BaseIntegratedAgent._add_workflow_edges` to incorporate the new agent

## Configuration Options

Each agent type supports various configuration options:

- **Integrated Agent**:
  - `max_iterations`: Maximum number of iterations in the workflow
  - `agent_types`: Types of agents to include
  - `reflection_enabled`: Whether to enable reflection capabilities
  - `fault_tolerance_level`: Level of fault tolerance (0-3)
  - `tools`: List of tools to make available to agents

- **Research Agent**:
  - `max_sources`: Maximum number of sources to consult
  - `min_relevance_score`: Minimum relevance score for results
  - `search_depth`: Depth of search (1-3)
  - `include_web_search`: Whether to include web search
  - `include_code_search`: Whether to include code search
  - `include_documentation`: Whether to include documentation

- **Planning Agent**:
  - `max_steps`: Maximum number of steps in a plan
  - `detail_level`: Level of detail (low, medium, high)
  - `include_constraints`: Whether to include constraints
  - `include_assumptions`: Whether to include assumptions

- **Reflection Agent**:
  - `quality_threshold`: Threshold for acceptable quality (0-1)
  - `evaluation_criteria`: Criteria to evaluate
  - `detailed_feedback`: Whether to provide detailed feedback