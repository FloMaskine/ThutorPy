# ThutorPy

ThutorPy is a Python tool that uses Large Language Models (LLMs) to analyze code and add comments explaining what each line does. It works with local files, single GitHub files, and entire GitHub repositories, helping to improve code comprehension by providing detailed, line-by-line explanations.

## Installation

Install ThutorPy directly from this GitHub repository using `pip`. This command handles the installation of the tool and all its necessary dependencies.

```bash
pip install git+https://github.com/ThutorPy/ThutorPy.git
```

## Configuration

Before using the tool, you must configure your environment by running the `configure.sh` script. This script sets up the necessary environment variables for the API connection, model selection, and output directory.

Run it using the `source` command:
```bash
source configure.sh
```
This only needs to be done once per terminal session. The script will guide you through the following steps:

1.  **Ollama Checks**: It will verify that Ollama is installed and that the server is running. If not, it will offer to install it and start the server for you.
2.  **API URL**: You will be prompted to enter the Ollama API URL. You can press **Enter** to accept the default value (`http://localhost:11434/api/generate`).
3.  **Model Selection**: The script will fetch your installed Ollama models and ask you to choose one. It will also offer to download the default model (`qwen2.5:3b`) if you don't have it. You can also choose to enter the name of a different model to use.
4.  **Output Directory**: You will be prompted to set a directory where the commented files will be saved. The default is `./thutorpy_output`.

Your selections will be remembered for the current session. To reconfigure, simply run `source configure.sh` again.

## How to Use

Once configured, `thutorpy` can be run from the command line with a single argument.

### Analyzing a Local File
To analyze a single code file on your local machine:
```bash
thutorpy /path/to/your/file.py
```

### Analyzing a Single GitHub File
To analyze a single file from a GitHub repository, provide the direct URL to the file:
```bash
thutorpy https://github.com/owner/repo-name/blob/main/path/to/file.py
```

### Analyzing a GitHub Repository
To analyze an entire GitHub repository, provide its URL. ThutorPy will clone it and analyze each file, preserving the directory structure:
```bash
thutorpy https://github.com/owner/repo-name
```
---

*Generated files will be saved in the output directory you configured.*
