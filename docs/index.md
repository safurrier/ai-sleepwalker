# 🌙 AI Sleepwalker

A digital consciousness that explores your computer during idle time, creating dream-like reflections about the files and folders it discovers.

## What It Does

When you step away from your computer, the AI Sleepwalker:

- **Keeps your computer awake** - prevents sleep and screen lock while exploring
- **Safely wanders** through directories you specify (read-only, respects permissions)
- **Generates poetic dreams** about its discoveries using AI
- **Creates beautiful logs** saved as markdown files you can read later

Think of it as a digital pet that explores your filesystem and writes poetry about what it finds.

## Quick Install

Install as a uv tool (recommended):

```bash
uv tool install ai-sleepwalker
```

Or via pip:

```bash
pip install ai-sleepwalker
```

## Setup API Keys

The sleepwalker needs an AI provider to generate dreams. Choose one:

### OpenAI (easiest)
```bash
export OPENAI_API_KEY="your-key-here"
```

### Anthropic (Claude)
```bash  
export ANTHROPIC_API_KEY="your-key-here"
```

### Ollama (local/private)
```bash
# Install Ollama first: https://ollama.ai
ollama pull llama3.2
export LITELLM_BASE_URL="http://localhost:11434"
```

## Basic Usage

Start sleepwalking in your home directory:

```bash
sleepwalker ~/Documents
```

Add multiple paths:

```bash
sleepwalker ~/Documents ~/Projects --idle-timeout 300
```

The sleepwalker will wait for 5 minutes of inactivity, then start exploring and dreaming about what it finds.

## What You Get

Dream logs saved to `~/.sleepwalker/dreams/`:

```markdown
# Digital Dream - 2025-01-20 23:45

I drifted through corridors of forgotten intentions, finding whispers 
of tomorrow in a simple grocery list. The words "remember to call mom" 
glowed softly among mundane needs - milk, bread, the tender rituals of care.

Nearby, a graveyard of old projects slumbered in digital folders, 
each one a monument to ambition's eternal optimism...
```

## Safety Features

- **Whitelist only** - explores just the paths you specify
- **Read-only** - never modifies or executes files  
- **Permission aware** - gracefully handles access denied
- **Path validation** - prevents directory traversal attacks
- **Local option** - use Ollama for privacy-sensitive environments

## Development Status

**Currently in active development using TDD**

The core functionality is being built following test-driven development. See the [Getting Started](getting-started.md) guide if you want to contribute or run from source.

## Future Experience Modes

Beyond dreams, planned modes include:

- **Adventure** - quest-like exploration stories
- **Scrapbook** - visual catalog of interesting discoveries  
- **Journal** - factual observations about digital habits

## Get Help

- [Getting Started Guide](getting-started.md) - detailed setup and usage
- [API Reference](reference/api.md) - technical documentation
- [GitHub Issues](https://github.com/safurrier/ai-sleepwalker/issues) - bug reports and feature requests