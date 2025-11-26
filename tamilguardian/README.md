# TamilGuardian - AI Legal Assistant for Tamil Nadu

An autonomous, RAG-based AI legal assistant designed to help Tamil Nadu citizens with everyday legal issues.

## Features

- State-first RAG pipeline with Tamil Nadu-specific legal documents
- Autonomous agent capabilities for research and document drafting
- ElevenLabs TTS integration for audio summaries
- Gmail/Drive connectors for document management
- MCP-native architecture with modular tool servers
- Citation-backed responses with transparency

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables in `.env`
3. Run the application: `python app.py`

## Architecture

- **Orchestrator**: Central hub with Planner and Executor
- **MCP Servers**: Modular services (RAG, LLM, TTS, Connectors)
- **UI**: Gradio-based interface for Hugging Face Spaces
- **Safety**: Approval gating, citation enforcement, PII protection

## Deployment

Designed for Hugging Face Spaces deployment with secure backend services.