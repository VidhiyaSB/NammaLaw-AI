import urllib.request
import json
from pathlib import Path

def extract_gradio_html():
    url = "https://www.gradio.app/main/guides/gradio-6-migration-guide"
    
    with urllib.request.urlopen(url) as response:
        html = response.read().decode('utf-8')
    
    # Save raw HTML
    Path("context").mkdir(exist_ok=True)
    with open("context/gradio_6_raw.html", 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Extracted HTML: {len(html)} characters saved to context/gradio_6_raw.html")

if __name__ == "__main__":
    extract_gradio_html()