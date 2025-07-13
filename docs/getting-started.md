# Getting Started

## Quick Install (Recommended)

Install AI Sleepwalker as a uv tool - this keeps it isolated and available everywhere:

```bash
uv tool install git+https://github.com/safurrier/ai-sleepwalker.git
```

Or clone and install locally:

```bash
git clone https://github.com/safurrier/ai-sleepwalker.git
cd ai-sleepwalker
uv tool install .
```

## Set Up API Keys

Choose an AI provider to generate dreams:

### Google Gemini (Recommended - Free Tier)

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/)
2. Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export GEMINI_API_KEY="your-actual-key-here"
```

3. Reload your shell: `source ~/.zshrc`

### OpenAI

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Set the environment variable:

```bash
export OPENAI_API_KEY="sk-your-actual-key-here"
```

### Anthropic (Claude)

1. Get an API key from [Anthropic Console](https://console.anthropic.com/)
2. Set the environment variable:

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### Ollama (Local/Private)

For completely private, offline use:

1. Install [Ollama](https://ollama.ai)
2. Pull a model: `ollama pull llama3.2`
3. Use the model directly: `sleepwalker ~/Documents --model ollama/llama3.2`

## First Run

Start sleepwalking in a safe directory:

```bash
sleepwalker ~/Documents
```

The sleepwalker will:
1. Wait for 5 minutes of inactivity (configurable)
2. Prevent your computer from sleeping
3. Explore the directory you specified
4. Generate dreams about what it finds
5. Save them to `~/.sleepwalker/dreams/`

## Common Options

```bash
# Custom idle timeout (seconds)
sleepwalker ~/Documents --idle-timeout 600

# Multiple directories
sleepwalker ~/Documents ~/Projects ~/Photos

# Specify AI model
sleepwalker ~/Documents --model gpt-4o-mini

# Dry run (no AI calls)
sleepwalker ~/Documents --dry-run
```

## Troubleshooting

### "No API key found"
Make sure you've set the environment variable and reloaded your shell.

### "Permission denied" errors
The sleepwalker can only read files you have access to. This is normal for system directories.

### Dreams aren't saving
Check that `~/.sleepwalker/dreams/` exists and is writable. The sleepwalker should create it automatically.

### Computer still goes to sleep
Some systems require additional permissions for sleep prevention. The sleepwalker will log warnings if it can't prevent sleep.

## What's Next?

- Read the [API Reference](reference/api.md) for advanced usage
- Check [GitHub Issues](https://github.com/safurrier/ai-sleepwalker/issues) for known issues
- Join discussions about new experience modes

## Development Setup

Want to contribute? See the [Developer Guide](developer-guide.md) for setup instructions and contribution guidelines.