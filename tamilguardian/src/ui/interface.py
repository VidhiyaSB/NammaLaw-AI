import gradio as gr
import asyncio
from typing import Optional, List
from ..orchestrator.main import NammaLawOrchestrator
import logging

logger = logging.getLogger(__name__)

def create_interface(orchestrator: NammaLawOrchestrator) -> gr.Blocks:
    """Create the main Gradio interface for TamilGuardian"""
    
    async def process_query(
        query: str,
        documents: Optional[List] = None,
        enable_audio: bool = False,
        language: str = "English"
    ):
        """Process user query and return results"""
        try:
            # Prepare user preferences
            preferences = {
                "enable_audio": enable_audio,
                "language": language
            }
            
            # Process documents if uploaded
            doc_bytes = []
            if documents:
                for doc in documents:
                    with open(doc.name, 'rb') as f:
                        doc_bytes.append(f.read())
            
            # Process the query
            result = await orchestrator.process_legal_query(
                query=query,
                documents=doc_bytes if doc_bytes else None,
                user_preferences=preferences
            )
            
            if not result.success:
                return f"Error: {result.error}", "", "", "", None
            
            # Format response
            summary = result.summary or "No summary available"
            
            # Format legal options
            options_text = ""
            if result.legal_options:
                options_text = "## Legal Options:\n\n"
                for i, option in enumerate(result.legal_options, 1):
                    options_text += f"### Option {i}: {option.title}\n"
                    options_text += f"{option.description}\n\n"
                    if option.steps:
                        options_text += "**Steps:**\n"
                        for step in option.steps:
                            options_text += f"- {step}\n"
                    if option.estimated_cost:
                        options_text += f"**Estimated Cost:** {option.estimated_cost}\n"
                    if option.timeline:
                        options_text += f"**Timeline:** {option.timeline}\n"
                    options_text += "\n---\n\n"
            
            # Format citations
            citations_text = ""
            if result.citations:
                citations_text = "## Sources:\n\n"
                for citation in result.citations:
                    citations_text += f"- **{citation.title}** ({citation.jurisdiction})\n"
                    citations_text += f"  Source: {citation.source_type} | Confidence: {citation.confidence:.2f}\n"
                    citations_text += f"  Excerpt: {citation.excerpt}\n\n"
            
            # Draft document
            draft = result.draft_document or "No draft generated"
            
            # Audio file
            audio_file = None
            if result.audio_url and enable_audio:
                audio_file = result.audio_url
            
            return summary, options_text, citations_text, draft, audio_file
            
        except Exception as e:
            logger.error(f"Interface error: {e}")
            return f"An error occurred: {str(e)}", "", "", "", None
    
    # Create the interface
    with gr.Blocks(
        title="NammaLaw AI - Legal Assistant",
        theme=gr.themes.Soft(),
        css="""
        .main-header { text-align: center; margin-bottom: 2rem; }
        .disclaimer { background-color: #fff3cd; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; }
        """
    ) as interface:
        
        # Header
        gr.HTML("""
        <div class="main-header">
            <h1>⚖️ NammaLaw AI</h1>
            <h3>AI Legal Assistant for Tamil Nadu</h3>
            <p>Get reliable legal guidance for everyday issues in Tamil Nadu</p>
        </div>
        """)
        
        # Disclaimer
        gr.HTML("""
        <div class="disclaimer">
            <strong>⚠️ Legal Disclaimer:</strong> This AI assistant provides general legal information only. 
            It is not a substitute for professional legal advice. For complex matters or court proceedings, 
            please consult a licensed attorney.
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # Input section
                gr.Markdown("## Describe Your Legal Issue")
                
                query_input = gr.Textbox(
                    label="Legal Question or Issue",
                    placeholder="Example: My landlord is not returning my security deposit after I moved out. What are my rights under Tamil Nadu law?",
                    lines=4
                )
                
                documents_input = gr.File(
                    label="Upload Documents (Optional)",
                    file_count="multiple",
                    file_types=[".pdf", ".docx", ".txt"]
                )
                
                with gr.Row():
                    enable_audio = gr.Checkbox(
                        label="Enable Audio Summary",
                        value=False
                    )
                    
                    language = gr.Dropdown(
                        label="Language",
                        choices=["English", "Tamil"],
                        value="English"
                    )
                
                submit_btn = gr.Button("Get Legal Guidance", variant="primary", size="lg")
            
            with gr.Column(scale=3):
                # Output section
                gr.Markdown("## Legal Analysis & Guidance")
                
                with gr.Tabs():
                    with gr.Tab("Summary"):
                        summary_output = gr.Markdown(label="Legal Summary")
                    
                    with gr.Tab("Options"):
                        options_output = gr.Markdown(label="Legal Options")
                    
                    with gr.Tab("Sources"):
                        citations_output = gr.Markdown(label="Legal Sources")
                    
                    with gr.Tab("Draft Document"):
                        draft_output = gr.Textbox(
                            label="Generated Legal Draft",
                            lines=15,
                            max_lines=20
                        )
                    
                    with gr.Tab("Audio"):
                        audio_output = gr.Audio(label="Audio Summary")
        
        # Examples section
        gr.Markdown("## Example Questions")
        
        examples = [
            "My employer is not paying overtime wages. What are my rights under Tamil Nadu labor laws?",
            "I bought a defective product and the seller refuses to refund. How can I file a consumer complaint?",
            "My landlord wants to evict me without proper notice. What should I do?",
            "I received a traffic challan that I believe is incorrect. How can I contest it?",
            "My neighbor's construction is causing damage to my property. What legal action can I take?"
        ]
        
        gr.Examples(
            examples=examples,
            inputs=query_input,
            label="Click on any example to try it"
        )
        
        # Event handlers
        def sync_process_query(*args):
            """Synchronous wrapper for async query processing"""
            return asyncio.run(process_query(*args))
        
        submit_btn.click(
            fn=sync_process_query,
            inputs=[query_input, documents_input, enable_audio, language],
            outputs=[summary_output, options_output, citations_output, draft_output, audio_output],
            api_visibility="public"
        )
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; margin-top: 2rem; padding: 1rem; border-top: 1px solid #eee;">
            <p><strong>NammaLaw AI</strong> - Powered by AI for Tamil Nadu Legal Assistance</p>
            <p>Built with ❤️ for the people of Tamil Nadu | 
            <a href="#privacy">Privacy Policy</a> | 
            <a href="#terms">Terms of Service</a></p>
        </div>
        """)
    
    return interface