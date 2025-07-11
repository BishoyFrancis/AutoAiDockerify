import subprocess
from utils import scan_project
import argparse
import os

def generate_dockerfile(context, model="phi3"):
    prompt = f"""
You are a professional DevOps engineer.

I will give you the contents of a small web application. Your task is to generate a working production-ready Dockerfile that can:

- Install necessary dependencies
- Expose the right port
- Run the app correctly using CMD or ENTRYPOINT
- do not add "```Dockerfile" at a start of the file or "```" at the end of the file
- Ensure the app runs in a production environment
- Use the best practices for Dockerfile creation
- Use the provided context to understand the application structure and dependencies
- install requirements.txt file if it exists

Make sure to include pip install or npm install if needed.

ONLY return the Dockerfile. No explanations.

### Project code:
{context}

# Dockerfile:
"""
    result = subprocess.run(
        ['ollama', 'run', model],
        input=prompt.encode(),
        stdout=subprocess.PIPE
    )
    return result.stdout.decode()

def save_dockerfile(content, path="Dockerfile"):
    with open(path, 'w') as f:
        f.write(content)
    print(f"✅ Dockerfile saved at: {path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-generate Dockerfile using local LLM")
    parser.add_argument('--path', required=True, help='Path to the project folder')
    args = parser.parse_args()
    directory = args.path.strip()
    # directory = input("📁 Enter path to your project directory (inside WSL): ").strip()
    context = scan_project(directory)
    print("🧠 Generating Dockerfile using Phi...")
    dockerfile = generate_dockerfile(context)
    save_dockerfile(dockerfile)
