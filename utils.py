import os,json

def detect_project_type(directory):
    """
    Detects the project language and framework based on the contents of the given directory.

    Returns:
        A tuple like ("python", "flask"), ("python", "django"), or ("generic", None).
    """
    lang, framework = "generic", None

    def file_contains(path, keywords):
        """
        Checks if any of the given keywords exist in the file.
        """
        try:
            with open(path, 'r', encoding='utf-16') as f:
                text = f.read().lower()
        except UnicodeError:
            # Fall back if encoding is not utf-16
            with open(path, 'r', errors='ignore') as f:
                text = f.read().lower()
        except:
            return False
        return any(kw in text for kw in keywords)

    # First, scan for 'requirements.txt' to identify Python + known frameworks
    for root, _, files in os.walk(directory):
        if "requirements.txt" in files:
            req_path = os.path.join(root, "requirements.txt")
            try:
                with open(req_path, 'r', encoding='utf-16') as f:
                    content = f.read().lower()
            except UnicodeError:
                with open(req_path, 'r', errors='ignore') as f:
                    content = f.read().lower()

            if "flask" in content:
                return "python", "flask"
            if "django" in content:
                return "python", "django"
            lang = "python"  # Python detected, but no known framework

    # Second, scan .py files for framework-specific import statements
    if lang == "python" or any(f.endswith(".py") for _, _, files in os.walk(directory) for f in files):
        for root, _, files in os.walk(directory):
            for f in files:
                if f.endswith(".py"):
                    path = os.path.join(root, f)
                    if file_contains(path, ["from flask", "import flask"]):
                        return "python", "flask"
                    if file_contains(path, ["from django", "import django"]):
                        return "python", "django"

        # If no known framework found, but Python files are present
        if lang == "python":
            return "python", None

    # Default fallback
    return lang, framework

        
    # Nodejs
    if "package.json" in files or any(f.endswith('.js') for f in files):
        # Detect Express
        for root, _, files in os.walk(directory):
            for f in files:
                path = os.path.join(root, f)
                if f == "server.js" or f == "app.js":
                    with open(path, "r", errors="ignore") as fp:
                        content = fp.read(200).lower()
                        if "express" in content:
                            return "node", "express"
        return "node", None                 
    # Java (Maven/Gradle)
    if "pom.xml" in files or any(f.endswith(".gradle") for f in files):
        return "java", "spring"
        # .NET
    if any(f.endswith(".csproj") for f in files):
        return "dotnet", None
    
    # C++
    if any(f.endswith(".cpp") for f in files):
        return "cpp", None
    
    return "generic", None

print(detect_project_type('test-flask-app'))