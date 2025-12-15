# ForumEngine - Agent Collaboration Mechanism

## Package Identity
ForumEngine is the agent collaboration mechanism of BettaFish multi-agent system. It monitors agent logs in real-time, facilitates LLM-hosted discussions between agents, and manages multi-turn conversations for collective intelligence and decision support.

Primary tech/framework: Python with real-time log monitoring, LLM integration for hosting discussions, and SocketIO for communication with the main Flask application.

## Setup & Run
```bash
# ForumEngine is automatically started by main system
python app.py  # ForumEngine is integrated and managed automatically

# Manual start (for testing)
python -c "from ForumEngine.monitor import start_forum_monitoring; start_forum_monitoring()"
```

## Patterns & Conventions

### File Organization
- `monitor.py` - Core forum monitoring and management logic
- `llm_host.py` - LLM implementation for forum hosting and moderation
- Log files: `../logs/forum.log` - Persistent storage for forum discussions

### Forum Monitoring Pattern
✅ DO: Use structured log monitoring for agent coordination:
```python
# Example from ForumEngine/monitor.py
class ForumMonitor:
    def __init__(self):
        self.log_file = Path("logs/forum.log")
        self.llm_host = LLMHost()
        self.agent_outputs = {}
    
    def monitor_agent_logs(self):
        # Monitor all agent log files for new outputs
        for agent_name in ['insight', 'media', 'query']:
            new_output = self.check_agent_log(agent_name)
            if new_output:
                self.process_agent_output(agent_name, new_output)
    
    def process_agent_output(self, agent_name: str, output: str):
        # Store agent output and trigger forum discussion
        self.agent_outputs[agent_name] = output
        
        # Check if forum discussion should be triggered
        if self.should_trigger_discussion():
            self.facilitate_discussion()
```

❌ DON'T: Use direct agent-to-agent communication:
```python
# Avoid this pattern
def direct_communication(self, agent1, agent2):
    # Direct communication breaks the forum-based architecture
    agent1.send_message_to(agent2, message)
```

### LLM Host Implementation
✅ DO: Implement structured forum hosting:
```python
# Example from ForumEngine/llm_host.py
class LLMHost:
    def __init__(self):
        self.llm_client = OpenAIClient()
        self.discussion_context = []
    
    def facilitate_discussion(self, agent_outputs: dict):
        # 1. Analyze agent outputs
        analysis = self.analyze_outputs(agent_outputs)
        
        # 2. Generate discussion prompt
        prompt = self.generate_discussion_prompt(analysis)
        
        # 3. Get LLM response as forum host
        host_response = self.llm_client.chat_completion(prompt)
        
        # 4. Log host response to forum
        self.log_to_forum("HOST", host_response)
        
        # 5. Prompt agents for further input
        self.prompt_agents_for_response(host_response)
```

### Log-Based Communication
✅ DO: Use structured logging for agent communication:
```python
# Format: [timestamp] [source] content
def log_agent_message(self, agent_name: str, message: str):
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] [{agent_name.upper()}] {message}"
    
    with open(self.log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')
    
    # Emit to frontend via SocketIO
    socketio.emit('forum_message', {
        'type': 'agent',
        'sender': f'{agent_name.title()} Engine',
        'content': message,
        'timestamp': timestamp,
        'source': agent_name.upper()
    })
```

## Touch Points / Key Files

- Forum monitor: `monitor.py` - Core forum monitoring and management
- LLM host: `llm_host.py` - Forum hosting and moderation logic
- Log management: `monitor.py` - Log file handling and parsing
- SocketIO integration: `monitor.py` - Real-time communication with frontend
- Agent coordination: `monitor.py` - Multi-agent discussion facilitation

## JIT Index Hints

- Find forum monitoring: `rg -n "monitor.*forum\|forum.*monitor" monitor.py`
- Find LLM hosting: `rg -n "class.*Host\|host.*discussion" llm_host.py`
- Find log parsing: `rg -n "parse.*log\|log.*format" monitor.py`
- Find agent coordination: `rg -n "facilitate\|coordinate\|discussion" monitor.py`
- Find SocketIO integration: `rg -n "socketio\|emit\|forum_message" monitor.py`

## Common Gotchas

- Forum log must be properly formatted for parsing: `[timestamp] [source] content`
- LLM host requires proper API key configuration in main config
- Agent outputs must be monitored in real-time for effective coordination
- Forum discussions should be triggered based on content analysis, not just timing
- Log file permissions must allow read/write access for all components
- SocketIO events must be properly formatted for frontend consumption

## Pre-PR Checks

```bash
# Test forum monitoring
python -c "from ForumEngine.monitor import test_forum_monitoring; test_forum_monitoring()"

# Test LLM hosting
python -c "from ForumEngine.llm_host import LLMHost; LLMHost().test_hosting()"

# Validate log parsing
python -c "from ForumEngine.monitor import test_log_parsing; test_log_parsing()"

# Check forum log format
python -c "from ForumEngine.monitor import validate_log_format; validate_log_format('logs/forum.log')"