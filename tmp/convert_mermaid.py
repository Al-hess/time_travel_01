import base64
import os
import urllib.request
import re
import sys

def convert_mermaid_to_png(md_file_path, output_png_path):
    print(f"Processing {md_file_path}...")
    if not os.path.exists(md_file_path):
        print(f"File not found: {md_file_path}")
        return

    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract Mermaid code block (different types: erDiagram, sequenceDiagram, etc.)
    # We look for any mermaid block
    match = re.search(r'```mermaid\s+(.*?)```', content, re.DOTALL)
    if not match:
        print(f"Could not find Mermaid block in {md_file_path}")
        return
    
    mermaid_code = match.group(1).strip()
    print(f"Found Mermaid code in {os.path.basename(md_file_path)}. Encoding...")
    
    # Encode to base64
    graph_bytes = mermaid_code.encode("utf8")
    base64_bytes = base64.urlsafe_b64encode(graph_bytes)
    base64_string = base64_bytes.decode("ascii")
    
    url = f"https://mermaid.ink/img/{base64_string}"
    print(f"Downloading image from {url}...")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    with open(output_png_path, 'wb') as out_f:
                        out_f.write(response.read())
                    print(f"Successfully saved PNG to {output_png_path}")
                    return
                else:
                    print(f"Error: Received status code {response.status}")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(2)
            else:
                print(f"All {max_retries} attempts failed for {output_png_path}")

if __name__ == "__main__":
    current_dir = os.getcwd()
    schemas_dir = os.path.join(current_dir, 'schemas')
    
    files_to_convert = [
        ('erd.md', 'erd.png'),
        ('schema.md', 'schema.png'),
        ('sequence.md', 'sequence.png')
    ]
    
    for md_name, png_name in files_to_convert:
        md_path = os.path.join(schemas_dir, md_name)
        png_path = os.path.join(schemas_dir, png_name)
        convert_mermaid_to_png(md_path, png_path)
