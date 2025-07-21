# ThutorPy

ThutorPy is a Python tool that uses Large Language Models (LLMs) to analyze your code and add comments explaining what each line does. It works with local files and entire GitHub repositories, helping to improve code comprehension by providing detailed, line-by-line explanations.

## Installation

You can install ThutorPy directly from GitHub using `pip`. This single command handles the installation of the tool and all its dependencies.

```bash
pip install git+https://github.com/FloMaskine/ThutorPy.git
```

## Configuration

After installing, you need to configure the tool. Run the following command and follow the on-screen prompts:

```bash
thutorpy-configure
```

This interactive setup will:

1. Check that Ollama is running.
2. Ask you to select an Ollama model to use for generating comments.
3. Ask you to specify a default directory to save the output files.

Your settings are saved to a configuration file in your home directory, so you only need to do this once.

## How to Use

Once configured, `thutorpy` can be run from the command line with a single argument: the path to a local file or the URL to a GitHub repository.

### Analyzing a Local File

```bash
thutorpy /path/to/your/file.py
```

### Analyzing a GitHub Repository

```bash
thutorpy https://github.com/owner/repo-name
```

---

Commented files will be saved in a unique, timestamped sub-folder within the output directory you configured. After each run, the tool will print the exact path to the results.
