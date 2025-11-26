# NammaLaw AI

AI-powered legal assistant for Tamil Nadu, built with Gradio 6.

## Features

- Legal query processing with AI orchestration
- Document upload and analysis
- Multi-language support (English/Tamil)
- Audio summaries
- Legal options and citations
- Draft document generation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd "NammaLaw AI"
```

2. Install dependencies:
```bash
pip install -r tamilguardian/requirements.txt
```

3. Set up environment variables:
```bash
cp tamilguardian/.env.example tamilguardian/.env
# Edit .env with your configuration
```

## Usage

Run the application:
```bash
cd tamilguardian
python app.py
```

The app will be available at http://localhost:7860

## Architecture

- **Orchestrator**: Main coordination component (`src/orchestrator/`)
- **UI**: Gradio-based interface (`src/ui/`)
- **MCP Servers**: Modular server components (`src/mcp_servers/`)

## Gradio 6 Migration

This application has been updated to be compatible with Gradio 6. See `context/gradio_6_migration_summary.json` for details.

## License

MIT License