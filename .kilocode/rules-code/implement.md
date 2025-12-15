# Implementation Guidelines for BettaFish Multi-Agent System

## Overview

This document provides implementation guidelines for the BettaFish multi-agent public opinion analysis system. It outlines the programming principles, systematic code protocols, and testing requirements that should be followed when developing or modifying the system.

## System Architecture Context

BettaFish is a multi-agent system consisting of:
- **Flask Orchestrator**: Main application server with SocketIO for real-time communication
- **InsightEngine**: Database mining and sentiment analysis agent
- **MediaEngine**: Multimodal content analysis with web search
- **QueryEngine**: Precise information search and query optimization
- **ReportEngine**: Intelligent report generation from all agent outputs
- **ForumEngine**: Agent collaboration mechanism
- **MindSpider**: Social media crawling system

## Programming Principles

### Multi-Agent System Design
- **agent_isolation: Each agent operates independently with minimal direct dependencies
- **parallel_execution: Agents should be designed to run simultaneously without interference
- **fault_tolerance: Individual agent failures should not bring down the entire system
- **communication_protocols: Use structured log outputs and SocketIO for inter-agent communication

### Data Processing and Analysis
- **data_integrity: Ensure data consistency across all agents and components
- **async_processing: Use non-blocking I/O throughout the system for performance
- **error_handling: Implement comprehensive error handling with retry mechanisms
- **scalability: Design components to handle increasing loads and data volumes

### Report Generation and Output
- **template_driven: Use template-based report generation for consistency
- **multi_format: Support both HTML and PDF output formats
- **streaming: Implement streaming for large report generation
- **intermediate_representation: Use IR to decouple content generation from rendering

## Systematic Code Protocol

### [Step: 1] Analyze Code
#### Dependency Analysis
When implementing changes, consider:
- Which agents will be affected by the change?
- What dependencies exist between components?
- Is this a local change or does it affect core orchestration logic?
- How will this change impact the Flask orchestrator?
- What cascading effects will this change have on the multi-agent workflow?

#### Flow Analysis
Before proposing changes:
- Conduct complete end-to-end flow analysis of the relevant use case
- Track data flow from user input through all agents to final report generation
- Consider impact on ForumEngine coordination and monitoring
- Analyze effect on real-time communication via SocketIO
- Document dependencies thoroughly, including specific usage in all engine directories

### [Step: 2] Plan Code
#### Structured Proposals
Provide proposals that specify:
1. **Files and Components**: What files, functions, or agents are being changed
2. **Change Necessity**: Bug fix, improvement, or new feature
3. **Direct Impact**: Which engines or components are directly affected
4. **Side Effects**: Potential impact on other agents or the orchestrator
5. **Tradeoffs**: Detailed explanation of any architectural tradeoffs

#### Multi-Agent Considerations
- How will changes affect agent coordination through ForumEngine?
- Will the change impact parallel execution of agents?
- Are there implications for real-time progress monitoring?
- How will report generation be affected?

### [Step: 3] Make Changes
#### Document Current State
- What's currently working in the multi-agent system?
- What's the current error or issue?
- Which agents, engines, or components will be affected?

#### Plan Single Logical Change at a Time
- One logical feature at a time across the entire system
- Fully resolve the change by accommodating appropriate changes in all affected agents
- Adjust all existing dependencies and issues created by the change
- Ensure architecture preservation: new code integrates seamlessly with existing multi-agent structure

#### Simulation Testing
- Simulate user interactions and agent workflows
- Perform dry runs of multi-agent coordination
- Trace calls through the Flask orchestrator and all agents
- Generate feedback on potential side effects across the system
- Do not proceed unless simulation passes and verifies existing functionality preservation

### [Step: 4] Perform Testing
#### Multi-Agent Testing Strategy
- Test individual agent functionality in isolation
- Test agent coordination through ForumEngine
- Test parallel execution and resource management
- Test real-time communication and progress monitoring
- Test end-to-end workflow from user input to report generation

#### Integration Testing
- Test Flask orchestrator with all agents
- Test database connections and data persistence
- Test report generation with all agent outputs
- Test error handling and recovery mechanisms

### [Step: 5] Loop and Implement
- Incorporate all changes systematically across the multi-agent system
- Verify changes and test them one by one
- Ensure no agent is left behind in the update process

### [Step: 6] Optimize the Implemented Code
- Optimize for multi-agent coordination performance
- Optimize database queries and data processing
- Optimize report generation and rendering
- Optimize real-time communication and streaming

## Testing Requirements

### Unit Testing
- Create unit tests for each agent's core functionality
- Test individual components within engines (nodes, tools, utilities)
- Test database operations and data processing
- Test LLM integrations and API calls

### Integration Testing
- Test agent communication and coordination
- Test Flask orchestrator with all components
- Test ForumEngine monitoring and moderation
- Test report generation from multiple agent outputs

### End-to-End Testing
- Test complete user workflows from query to report
- Test multi-agent parallel execution
- Test error scenarios and recovery
- Test performance under load

### Performance Testing
- Test system scalability with increasing data volumes
- Test concurrent user sessions and agent execution
- Test memory usage and resource management
- Test report generation performance with large datasets

## Component-Specific Guidelines

### Flask Orchestrator (app.py)
- Maintain clean separation between routing and business logic
- Use proper error handling and logging throughout
- Ensure SocketIO events are properly managed and cleaned up
- Implement proper session management for multi-user support

### Agent Implementation (InsightEngine, MediaEngine, QueryEngine)
- Follow consistent agent structure across all engines
- Implement proper state management and persistence
- Use structured logging for ForumEngine monitoring
- Ensure graceful degradation when external services fail

### ForumEngine
- Maintain real-time monitoring of all agent logs
- Implement proper LLM hosting and moderation
- Handle agent coordination conflicts gracefully
- Ensure speech synthesis and moderation work correctly

### ReportEngine
- Support multiple report templates and formats
- Implement streaming for large report generation
- Ensure proper IR management and rendering
- Handle PDF generation with layout optimization

### MindSpider
- Maintain support for 30+ social media platforms
- Implement proper rate limiting and error handling
- Ensure data quality and consistency
- Handle platform-specific requirements and changes

## Security Considerations

### Data Protection
- Implement proper encryption for sensitive data
- Use secure communication channels for all external API calls
- Validate all inputs using structured schemas
- Implement proper access controls and user isolation

### API Security
- Secure API keys and credentials management
- Implement proper authentication and authorization
- Use rate limiting and abuse prevention
- Monitor for suspicious activities and anomalies

## Deployment Guidelines

### Containerization
- Use multi-stage Docker builds for optimization
- Implement proper health checks and monitoring
- Use environment variables for configuration
- Ensure proper volume mounting for data persistence

### Environment Management
- Use separate configurations for development, testing, and production
- Implement proper logging and monitoring
- Use database migrations for schema changes
- Implement backup and recovery procedures

## Code Quality Standards

### Code Organization
- Follow consistent directory structure across all components
- Use clear and descriptive naming conventions
- Implement proper separation of concerns
- Use type hints and documentation strings

### Performance Standards
- Optimize database queries and connections
- Use async processing for I/O operations
- Implement proper caching strategies
- Monitor and optimize resource usage

### Documentation Standards
- Maintain comprehensive API documentation
- Use inline comments for complex logic
- Keep README files up to date
- Document deployment and configuration procedures
