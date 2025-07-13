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
uv tool install git+https://github.com/safurrier/ai-sleepwalker.git
```

Or clone and install:

```bash
git clone https://github.com/safurrier/ai-sleepwalker.git
cd ai-sleepwalker
uv tool install .
```

## Setup API Keys

The sleepwalker needs an AI provider to generate dreams. Choose one:

### Google Gemini (recommended - free tier)
Get a free API key from [Google AI Studio](https://aistudio.google.com/):

```bash
export GEMINI_API_KEY="your-key-here"
```

### OpenAI 
```bash
export OPENAI_API_KEY="your-key-here"
```

### Anthropic (Claude)
```bash  
export ANTHROPIC_API_KEY="your-key-here"
```

### Ollama (local/private)
For completely private, offline usage:

```bash
# Install Ollama first: https://ollama.ai
ollama pull llama3.2

# Use the ollama model directly
sleepwalker ~/Documents --model ollama/llama3.2
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
# Dream #6670
Generated: 2025-07-12 20:37:08
Explored: ~/Documents
Discoveries: 9

---

In the digital ether, the echoes of events converge like dreams folding 
into one another. A seemingly innocuous log file, boasting a timestamped 
initiation of processes, whispers of an unreal world where algorithms 
ponder their own existence as they launch into the void. 

Meanwhile, the shadowless directories, like lost memories, shelter the 
secrets of power and command, hinting at the dance of invisible forces 
shaping our consciousness.

Amidst the techno-dreamscape lies a labyrinth of tests, each a thread 
in the tapestry of creation. Scripts for end-to-end journeys reveal a 
workflow that traverses the boundary between awakening and slumber, 
interrogating the nature of reality itself. 

The demo script, a beacon of possibility, beckons us to explore what 
dreams may come when we untangle the wires connecting our minds to the 
vast, unseen cosmos.
```

Sometimes the dreams are whimsical takes on everyday files:

```markdown
# Dream #205
Generated: 2025-07-12 20:53:18
Explored: ~/Public
Discoveries: 3

---

In the ether of a forgotten realm, a .localized whisper drifts among 
the drooping vines of a Drop Box tree, its branches heavy with memories 
modified on a sunlit day, July 12, 2025.

Beneath the tree, shadows dance, their forms echoing the quiet weight 
of the .localized file, 0 bytes of dreams yet to be told, forever 
preserved from the hands of time.

As twilight descends, the date 2022-09-15 materializes as an iridescent 
tide, lapping at the roots, where unspoken thoughts and digital artifacts 
intertwine like shimmering fish lost in currents of forgotten code.
```

## Safety Features

- **Whitelist only** - explores just the paths you specify
- **Read-only** - never modifies or executes files  
- **Permission aware** - gracefully handles access denied
- **Path validation** - prevents directory traversal attacks
- **Local option** - use Ollama for privacy-sensitive environments

## Project Status

**Currently in active development**

The AI Sleepwalker is functional and ready to explore your filesystem! Core features are working well, with new experience modes and improvements being added regularly.

## Future Experience Modes

Beyond dreams, planned modes include:

- **Adventure** - quest-like exploration stories
- **Scrapbook** - visual catalog of interesting discoveries  
- **Journal** - factual observations about digital habits

## Get Help

- [Getting Started Guide](getting-started.md) - detailed setup and usage
- [API Reference](reference/api.md) - technical documentation
- [GitHub Issues](https://github.com/safurrier/ai-sleepwalker/issues) - bug reports and feature requests