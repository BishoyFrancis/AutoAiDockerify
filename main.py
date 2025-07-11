import subprocess
from utils import scan_project
import argparse
import os
import logging

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
    logging.info(f"✅ Dockerfile saved at: {path}")

def dockerfile_validation(path="Dockerfile"):
    if not os.path.exists(path):
        print(f"❌ Dockerfile not found at: {path}")
        logging.error(f"❌ Dockerfile not found at: {path}")
        return False
    with open(path, 'r') as f:
        content = f.read()
        if "FROM" not in content or "CMD" not in content:
            print("❌ Dockerfile is missing required instructions.")
            logging.error("❌ Dockerfile is missing required instructions.")
            return False
        print("🔍 Testing Dockerfile with docker build...")
        logging.info("🔍 Testing Dockerfile with docker build...")
    try:
        build_result = subprocess.run(
        ['docker', 'build', '-f', path, '.'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker build failed: {e.stderr.decode()}")
        logging.error(f"❌ Docker build failed: {e.stderr.decode()}")
        return False
    return build_result.returncode == 0, build_result.stderr.decode()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-generate Dockerfile using local LLM")
    parser.add_argument('--path', required=True, help='Path to the project folder')
    parser.add_argument('--model', default='phi3', help='Ollama model to use (default: phi3)')
    parser.add_argument('--output', default='Dockerfile', help='Output Dockerfile name (default: Dockerfile)')
    args = parser.parse_args()
    directory = args.path.strip()
    # directory = input("📁 Enter path to your project directory (inside WSL): ").strip()
    context = scan_project(directory)
    print("🧠 Generating Dockerfile using Phi...")
    logging.info("🧠 Generating Dockerfile using Phi...")
    dockerfile = generate_dockerfile(context, model=args.model)
    save_dockerfile(dockerfile, path=args.output)
    valid, error = dockerfile_validation(args.output)
    if valid:
        print("✅ Dockerfile built successfully!")
        logging.info("✅ Dockerfile built successfully!")
    else:
        print("❌ Dockerfile build failed. Error:")
        logging.error(error)