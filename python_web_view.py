import subprocess
import os

def open_markdown_viewer(md_path):
    try:
        # Create simple HTML viewer
        html = f"""<!DOCTYPE html>
        <html>
        <head>
            <title>Audit Report</title>
            <meta charset="utf-8">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css@5/github-markdown.min.css">
            <style>.markdown-body {{ margin: 2em auto; max-width: 900px; }}</style>
        </head>
        <body class="markdown-body">
            {{content}}
        </body>
        </html>"""
        
        # Convert MD to HTML
        import markdown
        with open(md_path, 'r') as f:
            content = markdown.markdown(f.read())
        html = html.replace('{content}', content)
        
        # Save and open
        html_path = os.path.splitext(md_path)[0] + '.html'
        with open(html_path, 'w') as f:
            f.write(html)
        subprocess.run(['start', html_path], shell=True)
    except ImportError:
        print("Install markdown: pip install markdown")

# Usage after audit completes
open_markdown_viewer("U:\\AI Github Auditor\\outputs\\Gemini_based_chatbot_audit_20250808_000507.md")