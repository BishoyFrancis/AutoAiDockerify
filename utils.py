import os

def scan_project(directory):
    context = ""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', 'requirements.txt', 'package.json', 'main.cpp', 'index.js', 'app.js', '.csproj', 'pom.xml')):
                try:
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        context += f"\n\n# File: {file}\n{content}"
                except Exception as e:
                    print(f"Error reading {file}: {e}")
    return context[:8000]
