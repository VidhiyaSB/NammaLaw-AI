import gradio as gr
import asyncio
from src.orchestrator.main import NammaLawOrchestrator
from src.ui.interface import create_interface
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    """Main entry point for NammaLaw AI application"""
    orchestrator = NammaLawOrchestrator()
    
    # Create Gradio interface
    interface = create_interface(orchestrator)
    
    # Launch the app
    interface.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )

if __name__ == "__main__":
    main()