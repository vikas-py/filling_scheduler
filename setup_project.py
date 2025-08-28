import os

# Folder and file structure
structure = {
    "filling_scheduler": {
        "main.py": "",
        "requirements.txt": "pandas>=2.0\n",
        "README.md": "# Filling Scheduler\n\nGenerated project skeleton.\n",
        ".gitignore": """# Python
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/
.eggs/
*.log

# Virtual env
.venv/
env/
venv/

# IDEs
.vscode/
.idea/

# Outputs
output/
""",
        "fillscheduler": {
            "__init__.py": "",
            "config.py": "",
            "models.py": "",
            "io_utils.py": "",
            "heuristics.py": "",
            "scheduler.py": "",
            "validate.py": "",
            "reporting.py": "",
        },
        "examples": {
            "lots.csv": "Lot ID,Type,Vials\n"  # add headers only
        },
    }
}


def create_structure(base, tree):
    for name, content in tree.items():
        path = os.path.join(base, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)


if __name__ == "__main__":
    create_structure(".", structure)
    print("✅ Project structure created in ./filling_scheduler")
