import argparse
import sys
import os
import tempfile
import subprocess
import datetime
import requests
from . import core

def is_github_url(url):
    """Check if the URL is a GitHub URL."""
    return url.startswith(('http://', 'https://')) and 'github.com' in url

def is_github_file_url(url):
    """Check if the URL is a GitHub file URL."""
    return is_github_url(url) and '/blob/' in url

def get_raw_github_url(file_url):
    """Convert a GitHub file URL to its raw content URL."""
    return file_url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')

def process_file(file_path, output_dir):
    """Processes a single file."""
    print(f"Analyzing: {file_path}")
    output_path = os.path.join(output_dir, os.path.basename(file_path))
    core.analyze_code(file_path, output_path)

def process_github_file(file_url, output_dir):
    """Downloads and processes a single file from GitHub."""
    try:
        raw_url = get_raw_github_url(file_url)
        print(f"Downloading file: {raw_url}")
        response = requests.get(raw_url)
        response.raise_for_status()
        print("File downloaded successfully.")

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=os.path.basename(file_url)) as temp_file:
            temp_file.write(response.text)
            temp_file_path = temp_file.name
        
        process_file(temp_file_path, output_dir)
        os.unlink(temp_file_path)

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}", file=sys.stderr)
        sys.exit(1)

def process_repository(repo_url, output_dir):
    """Clones a repository and processes its files."""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Cloning repository: {repo_url}")
            subprocess.run(['git', 'clone', repo_url, temp_dir], check=True, capture_output=True, text=True)
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
                        core.analyze_code(file_path, output_path)

                    except (UnicodeDecodeError, IsADirectoryError):
                        print(f"Skipping binary file: {file_path}", file=sys.stderr)
                        continue
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Analyze a file or GitHub repository and save the commented code."
    )
    parser.add_argument("path", help="The local file path or GitHub repository URL to analyze.")
    args = parser.parse_args()

    output_dir = os.environ.get("THUTORPY_OUTPUT_DIR")
    if not output_dir:
        print("Error: Output directory not configured. Please run 'source configure.sh' first.", file=sys.stderr)
        sys.exit(1)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    sanitized_path = os.path.basename(args.path).replace('.git', '')
    execution_dir_name = f"{timestamp}_{sanitized_path}"
    execution_dir = os.path.join(output_dir, execution_dir_name)
    
    os.makedirs(execution_dir, exist_ok=True)
    abs_execution_dir = os.path.abspath(execution_dir)
    print(f"Output will be saved to: {abs_execution_dir}")

    if is_github_file_url(args.path):
        process_github_file(args.path, execution_dir)
    elif is_github_url(args.path):
        process_repository(args.path, execution_dir)
    elif os.path.isfile(args.path):
        process_file(args.path, execution_dir)
    else:
        print(f"Error: The path '{args.path}' is not a valid file or GitHub repository URL.", file=sys.stderr)
        sys.exit(1)

    # --- Final User Message ---
    print("\n" + "="*50)
    print("✅ Analysis complete!")
    print(f"Commented files are saved in: {abs_execution_dir}")
    print("To navigate to the output directory, you can run:")
    print(f"cd {abs_execution_dir}")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
