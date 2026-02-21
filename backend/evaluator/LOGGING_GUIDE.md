# Logging Guide

## Overview

We now have comprehensive logging throughout the application for better observability and debugging.

## Features

✅ **Color-coded console output** - Different colors for different log levels
✅ **Detailed formatting** - Timestamp, level, module, line number, and message
✅ **File logging** - Optional logging to files
✅ **Exception tracking** - Full stack traces for errors

## Usage

### Basic Setup

```python
from backend.evaluator.app_logger import setup_logger

# Create a logger for your module
logger = setup_logger(__name__)

# Use it
logger.info("Application started")
logger.debug("Debug information")
logger.warning("Warning message")
logger.error("Error occurred")
```

### Log Levels

```python
import logging

# Set different log levels
logger = setup_logger(__name__, level=logging.DEBUG)   # Show everything
logger = setup_logger(__name__, level=logging.INFO)    # Default
logger = setup_logger(__name__, level=logging.WARNING) # Warnings and above only
```

**Level meanings:**
- `DEBUG (10)`: Detailed diagnostic information
- `INFO (20)`: General informational messages
- `WARNING (30)`: Warning messages
- `ERROR (40)`: Error messages
- `CRITICAL (50)`: Critical errors

### With File Output

```python
logger = setup_logger(__name__, level=logging.DEBUG, log_file="logs/myapp.log")
```

### Exception Logging

```python
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)  # exc_info=True adds stack trace
```

## Current Implementation

### API Layer (`apis/routes/chat_api.py`)
- Logs all incoming requests
- Logs agent actions and results
- Logs errors with full stack traces
- Uses emoji indicators for easy scanning

### Agent Layer (`backend/agents/`)
- `ChatAgent`: Logs initialization, LLM calls, intent classification
- `RetrievalAgent`: Logs search operations, results count, errors

## Log Output Example

```
18:45:32 | INFO     | apis.routes.chat_api:19 | ✓ ChatAgent initialized successfully
18:45:35 | INFO     | apis.routes.chat_api:28 | 📨 Received chat request: 'Find Python developers...'
18:45:35 | DEBUG    | apis.routes.chat_api:30 | 🤖 Running ChatAgent...
18:45:35 | INFO     | backend.agents.chat_agent:20 | 🤖 ChatAgent.run() called with message: 'Find Python developers...'
18:45:35 | DEBUG    | backend.agents.chat_agent:23 | Loading intent classification prompt...
18:45:36 | DEBUG    | backend.agents.chat_agent:30 | Calling LLM for intent classification...
18:45:37 | INFO     | backend.agents.chat_agent:39 | ✓ Intent parsed: search (confidence: 0.95)
18:45:37 | INFO     | backend.agents.chat_agent:52 | 🔍 Search intent detected, delegating to RetrievalAgent...
18:45:37 | INFO     | backend.agents.retrieval_agent:12 | 🔍 RetrievalAgent.run() called
18:45:37 | DEBUG    | backend.agents.retrieval_agent:21 | Search params: query='Python developers', filters=None, limit=10
18:45:38 | INFO     | backend.agents.retrieval_agent:30 | ✓ Search completed: 5 results found
18:45:38 | INFO     | apis.routes.chat_api:42 | 🔍 Search action - found 5 candidates
18:45:38 | INFO     | apis.routes.chat_api:52 | ✓ Returning search response with 5 candidates
```

## Emoji Legend

- 📨 Incoming request
- 🤖 Agent operation
- 🔍 Search operation
- 💬 Chat response
- ✓ Success
- ✗ Failure
- ⚠️ Warning
- 📦 Data returned
- 📭 Empty result

## Tips

1. **Use DEBUG level during development**:
   ```python
   logger = setup_logger(__name__, level=10)  # or logging.DEBUG
   ```

2. **Use INFO level in production**:
   ```python
   logger = setup_logger(__name__, level=20)  # or logging.INFO
   ```

3. **Log function entry/exit for complex flows**:
   ```python
   def complex_function(param):
       logger.debug(f"Entering complex_function with param={param}")
       # ... logic ...
       logger.debug(f"Exiting complex_function with result={result}")
       return result
   ```

4. **Always use exc_info=True for exceptions**:
   ```python
   logger.error("Error message", exc_info=True)  # Includes full stack trace
   ```

## Troubleshooting

### Not seeing logs?
- Check the log level - DEBUG (10) shows everything, INFO (20) hides debug messages
- Make sure you're calling `setup_logger(__name__)` at the top of your module

### Too much output?
- Increase the log level to WARNING (30) or ERROR (40)
- Remove DEBUG level from modules you're not actively debugging

### Want to log to a file?
```python
logger = setup_logger(__name__, log_file="logs/app.log")
```
