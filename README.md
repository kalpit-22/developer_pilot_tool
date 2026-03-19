# DevPilot

An autonomous multi-agent system that takes a plain-English request and
automatically plans, writes, tests, and reviews Python code.

## How It Works

```
Your Request
     |
     v
  Planner  ->  breaks request into ordered tasks
     |
     v
  Coder    ->  writes code using file read/write tools
     |
     v
  Executor ->  runs code in a sandbox, captures output
     |
     v
  Reviewer ->  approves or rejects with feedback
     |         (loops back to Coder if rejected, up to 3 retries)
     v
  output/  ->  final files saved to disk
```

## Agents

| Agent | Role |
|---|---|
| Planner | Breaks the request into 2-3 focused coding tasks |
| Coder | Writes complete Python files using tool calling |
| Executor | Runs each file in an isolated workspace sandbox |
| Reviewer | Reads code + output, approves or gives feedback |

## Project Structure

```
devpilot/
├── main.py                  # Entry point
├── agents/
│   ├── base.py              # DeepSeek client + tool calling loop
│   ├── planner.py           # Task decomposition
│   ├── coder.py             # Code generation with file tools
│   ├── executor.py          # Subprocess sandbox
│   └── reviewer.py          # Code review + approval
├── core/
│   └── orchestrator.py      # Pipeline coordinator
├── workspace/               # Execution sandbox (auto-created)
└── output/                  # Generated files (auto-created)
```

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/devpilot
cd devpilot
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create a `.env` file:
```
DEEPSEEK_API_KEY=your_key_here
```

Get your key at [platform.deepseek.com](https://platform.deepseek.com) (~$25 free credits on signup)

## Usage

Edit `main.py` with your request:

```python
await orchestrator.run("Build a CLI todo app with add, list, and delete commands")
```

Then run:
```bash
python main.py
```

Generated files are saved to `output/`.

## Example Requests

```
Build a password generator with configurable length and character sets
Build a word counter that reads a file and shows the top 10 most frequent words
Build a student grade tracker that calculates averages and shows a leaderboard
Build a file organizer that sorts files into subdirectories by extension
Build a simple expense tracker that saves to JSON
```

## Requirements

- Python 3.10+
- `openai` — DeepSeek API client
- `python-dotenv` — loads API key from .env

## Cost

About $0.005 per run using `deepseek-chat`.

## License

MIT
