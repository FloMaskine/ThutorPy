import argparse
import sys
import os
import tempfile
import subprocess
import datetime
from . import core
from . import config as app_config

def is_git_repo(url):
    return url.startswith(('http://', 'https://')) and 'github.com' in url

def process_file(file_path, output_dir, config):
    print(f"Analyzing: {file_path}")
    output_path = os.path.join(output_dir, os.path.basename(file_path))
    core.analyze_code(file_path, output_path, config)

def process_repository(repo_url, output_dir, config):
    try:
        # Check if the repository exists before trying to clone
        result = subprocess.run(
            ['git', 'ls-remote', repo_url],
            check=False,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error: The repository at '{repo_url}' does not seem to exist.", file=sys.stderr)
            sys.exit(1)

        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Cloning repository: {repo_url}")
            result = subprocess.run(
                ['git', 'clone', repo_url, temp_dir], 
                check=False,
                capture_output=True, 
                text=True
            )
            
            if result.returncode != 0:
                print(f"Error cloning repository. Please check the URL and your permissions.", file=sys.stderr)
                print(f"Git error: {result.stderr}", file=sys.stderr)
                sys.exit(1)

            print("Repository cloned successfully.")
            for root, _, files in os.walk(temp_dir):
                if '.git' in root.split(os.sep):
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            f.read(1024)
                        relative_path = os.path.relpath(file_path, temp_dir)
                        output_path = os.path.join(output_dir, relative_path)
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        print(f"Analyzing: {file_path}")
                        core.analyze_code(file_path, output_path, config)
                    except (UnicodeDecodeError, IsADirectoryError):
                        print(f"Skipping binary file: {file_path}", file=sys.stderr)
                        continue
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Analyze a file or GitHub repository and save the commented code.")
    parser.add_argument("path", help="The local file path or GitHub repository URL to analyze.")
    args = parser.parse_args()

    config = app_config.load_config()
    output_dir = config["THUTORPY_OUTPUT_DIR"]

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    sanitized_path = os.path.basename(args.path).replace('.git', '')
    execution_dir_name = f"{timestamp}_{sanitized_path}"
    execution_dir = os.path.join(output_dir, execution_dir_name)
    
    os.makedirs(execution_dir, exist_ok=True)
    abs_execution_dir = os.path.abspath(execution_dir)
    print(f"Output will be saved to: {abs_execution_dir}")

    if is_git_repo(args.path):
        process_repository(args.path, execution_dir, config)
    elif os.path.isfile(args.path):
        process_file(args.path, execution_dir, config)
    else:
        print(f"Error: The path '{args.path}' is not a valid file or GitHub repository URL.", file=sys.stderr)
        sys.exit(1)

    print("\n" + "="*50)
    print("✅ Analysis complete!")
    print(f"Commented files are saved in: {abs_execution_dir}")
    print(f"To navigate to the output directory, you can run:\ncd {abs_execution_dir}")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()