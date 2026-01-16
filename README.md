# Pypestream QA Agent

AI-powered automated QA testing agent for Pypestream solutions. Uses vision models to navigate and test chatbot flows.

## Features

- 🤖 **Vision-Based AI**: Uses GPT-4 Vision, Claude, or Gemini to understand and interact with the UI
- 🎯 **Automated Testing**: Navigates through Pypestream flows automatically
- 📸 **Screenshot Capture**: Documents each step with screenshots
- 🧠 **Learning System**: Learns from successful actions to improve over time
- ⏸️ **Pause/Resume**: Control the agent mid-flow
- 🔄 **Reload Detection**: Automatically re-analyzes after page reloads
- 👆 **Manual Assist**: Train the AI by clicking the correct elements when stuck

## Installation

```bash
# Clone the repository
git clone https://github.com/bmichals-ps/pypestream-qa-agent.git
cd pypestream-qa-agent

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Usage

### Launch with Welcome Screen
```bash
export OPENAI_API_KEY="your-api-key"
python browser_control_agent.py
```

This opens a welcome screen where you can paste a Pypestream solution URL.

### Launch with Pre-loaded URL
```bash
export OPENAI_API_KEY="your-api-key"
python browser_control_agent.py "https://preview.pypestream.com/..."
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--provider` | Vision provider: `openai` (default), `anthropic`, or `gemini` |
| `--model` | Model name (default: `gpt-4.1-mini`) |
| `--smooth` | Use headless browser for cleaner screenshots |
| `--assist` | Enable manual assist when stuck |
| `--work-dir` | Directory for logs/screenshots/reports |

## Environment Variables

- `OPENAI_API_KEY` - Required for OpenAI provider
- `ANTHROPIC_API_KEY` - Required for Anthropic provider  
- `GEMINI_API_KEY` - Required for Gemini provider
- `VISION_PROVIDER` - Default provider (openai/anthropic/gemini)
- `VISION_MODEL` - Default model name

## UI Controls

- **Start Testing**: Begin the automated QA flow
- **Pause/Resume**: Pause the agent mid-flow
- **Reload**: Reload the solution and re-analyze
- **Change URL**: Return to welcome screen to test a different solution

## Output

- `screenshots/` - Screenshots of each step
- `logs/` - Execution logs
- `reports/` - JSON reports with test results
- `learned/` - Learned actions for each solution

## License

MIT
