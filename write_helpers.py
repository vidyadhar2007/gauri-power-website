
import os, base64

def write_b64(path, b64_content):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    content = base64.b64decode(b64_content).decode('utf-8')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully wrote {path} ({len(content)} chars)")
