from setuptools import setup, find_packages

# Read the requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="thutorpy",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "thutorpy=thutorpy.main:main",
            "thutorpy-configure=thutorpy.config:configure",
        ],
    },
    author="FloMaskine and Gemini",
    author_email="",
    description="A language-agnostic code commenter using Ollama.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/FloMaskine/ThutorPy",  # Replace with your repo URL
)
