import subprocess
from utils import scan_project, detect_project_type
import argparse
import os
import logging

def generate_dockerfile(context, model="phi3" , lang="generic", framework=None):
    # # build a custom preamble
    intro = f"You are a DevOps engineer. You will generate a Dockerfile for a {lang} application"
    if framework:
        intro += f" using the {framework} framework."
    intro += ".\nThe Dockerfile should be production-ready and follow best practices."
    prompt = intro + """
    Based on the following project files, generate a production-ready Dockerfile.
Only return the Dockerfile, no extra text.
""" + context + "\n #Dockerfile:\n"
    
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

def fix_prompt(model,broken_dockerfile):
    print("🔁 Trying to fix the Dockerfile using the model...")
    fix_prompt = f"""
    You are a DevOps expert. The following Dockerfile is broken or incomplete.
    Fix it and return only the corrected Dockerfile.

    Broken Dockerfile:
    {broken_dockerfile}

    """
    result = subprocess.run(
    ['ollama', 'run', model],
    input=fix_prompt.encode(),
    stdout=subprocess.PIPE
    )
    return result.stdout.decode()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-generate Dockerfile using local LLM")
    parser.add_argument('--path', required=True, help='Path to the project folder')
    parser.add_argument('--model', default='phi3', help='Ollama model to use (default: phi3)')
    parser.add_argument('--output', default='Dockerfile', help='Output Dockerfile name (default: Dockerfile)')
    args = parser.parse_args()
    directory = args.path.strip()
    # directory = input("📁 Enter path to your project directory (inside WSL): ").strip()
    context = scan_project(directory)
    lang, framework = detect_project_type(args.path)
    print("🧠 Generating Dockerfile using Phi...")
    logging.info("🧠 Generating Dockerfile using Phi...")
    dockerfile = generate_dockerfile(context, model=args.model , lang=lang, framework=framework)
    save_dockerfile(dockerfile, path=args.output)
    valid, error = dockerfile_validation(args.output)
    if valid:
        print("✅ Dockerfile built successfully!")
        logging.info("✅ Dockerfile built successfully!")
    else:
        logging.error(error)
        choice = input("🔁 Do you want the model to try fixing it? (y/n): ").strip().lower()
        if choice == 'y':
            fixed_dockerfile = fix_prompt(args.model, dockerfile)
            save_dockerfile(fixed_dockerfile, path=args.output)
            valid, error = dockerfile_validation(args.output)
            if valid:
                print("✅ Fixed Dockerfile built successfully!")
                logging.info("✅ Fixed Dockerfile built successfully!")
            else:
                print("❌ Still Failed , Here is the error:")
                print(error)
                logging.error("❌ Failed to fix the Dockerfile.")