# Development Workflow

## Edit-Validation Loop

1. **Edit**: Make changes to the codebase
2. **Validate**:
   - Run `~/.local/bin/uv run ruff check .` - Check code style and linting
   - Run `~/.local/bin/uv run pyright` - Type checking
   - Run `~/.local/bin/uv run pytest` - Execute tests

## Architecture

Python CLI application for high-accuracy audio transcription and diarization:

- `verbatim/` - Main package directory
  - `transcript/` - Transcript processing and formatting
  - `models.py` - Core data models
  - `config.py` - Configuration management
  - `env.py` - Environment variable handling
  - `log.py` - Logging utilities
- `tests/` - Test suite including evaluation metrics
- `run.py` - CLI entry point

The application integrates multiple ML models (Whisper variants, Pyannote) for transcription and speaker diarization with support for voice isolation, mixed languages, and GPU acceleration.

## Environment Setup

Sync dependencies:
```bash
~/.local/bin/uv sync
```

For CUDA GPU support:
```bash
~/.local/bin/uv sync --extra cuda-gpu
```

Run CLI:
```bash
~/.local/bin/uv run verbatim [options]
```
