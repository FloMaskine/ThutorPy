import argparse # Imports the library for parsing command-line arguments.
import sys # Imports the library for interacting with the Python interpreter.
import os # Imports the library for interacting with the operating system.
import tempfile # Imports the library for creating temporary files and directories.
import subprocess # Imports the library for running external commands.
import datetime # Imports the library for working with dates and times.
from . import core # Imports the core analysis functions from the local 'core' module.

def is_git_repo(url): # Defines a function to check if a URL is a GitHub repository.
    """Check if the URL is a git repository.""" # This is a docstring explaining what the function does.
    return url.startswith(('http://', 'https://')) and 'github.com' in url # Returns true if the URL starts with http/https and contains 'github.com'.

def process_file(file_path, output_dir): # Defines the function to process a single local file.
    """Processes a single file.""" # This is a docstring explaining what the function does.
    print(f"Analyzing: {file_path}") # Prints a message indicating which file is being analyzed.
    output_path = os.path.join(output_dir, os.path.basename(file_path)) # Constructs the full output path for the commented file.
    core.analyze_code(file_path, output_path) # Calls the main analysis function to generate and save the commented code.

def process_repository(repo_url, output_dir): # Defines the function to process a GitHub repository.
    """Clones a repository and processes its files.""" # This is a docstring explaining what the function does.
    try: # Starts a block to handle potential errors during the process.
        with tempfile.TemporaryDirectory() as temp_dir: # Creates a temporary directory that will be automatically cleaned up.
            print(f"Cloning repository: {repo_url}") # Informs the user that the cloning process is starting.
            subprocess.run(['git', 'clone', repo_url, temp_dir], check=True, capture_output=True, text=True) # Runs the 'git clone' command to download the repository.
            print("Repository cloned successfully.") # Confirms that the repository has been cloned.

            for root, _, files in os.walk(temp_dir): # Starts a loop to walk through all files and directories in the cloned repo.
                if '.git' in root.split(os.sep): # Checks if the current directory is part of the '.git' folder.
                    continue # Skips the '.git' directory to avoid analyzing internal Git files.
                for file in files: # Starts a loop through all the files in the current directory.
                    file_path = os.path.join(root, file) # Creates the full path to the current file.
                    try: # Starts a block to handle errors for individual file processing.
                        with open(file_path, 'r', encoding='utf-8') as f: # Opens the file in read mode with UTF-8 encoding.
                            f.read(1024) # Reads a small portion of the file to check if it's a text file.
                        
                        relative_path = os.path.relpath(file_path, temp_dir) # Gets the file's path relative to the repository root.
                        output_path = os.path.join(output_dir, relative_path) # Creates the corresponding path in the output directory.
                        os.makedirs(os.path.dirname(output_path), exist_ok=True) # Creates the necessary subdirectories in the output folder.
                        
                        print(f"Analyzing: {file_path}") # Prints a message indicating which file is being analyzed.
                        core.analyze_code(file_path, output_path) # Calls the main analysis function for the file.

                    except (UnicodeDecodeError, IsADirectoryError): # Catches errors specifically from the 'git clone' command.
                        print(f"Skipping binary file: {file_path}", file=sys.stderr) # Prints a message that a binary file is being skipped.
                        continue # Continues to the next file in the loop.
    except subprocess.CalledProcessError as e: # Catches errors specifically from the 'git clone' command.
        print(f"Error cloning repository: {e.stderr}", file=sys.stderr) # Prints the specific error message from the failed git command.
        sys.exit(1) # Exits the script with an error code.
    except Exception as e: # Catches any other general exceptions that might occur.
        print(f"An error occurred: {e}", file=sys.stderr) # Prints a generic error message for other issues.
        sys.exit(1) # Exits the script with an error code.

def main(): # Defines the main function that runs when the script is executed.
    parser = argparse.ArgumentParser( # Creates a new command-line argument parser.
        description="Analyze a file or GitHub repository and save the commented code." # Sets the description for the tool.
    ) # Finishes the parser definition.
    parser.add_argument("path", help="The local file path or GitHub repository URL to analyze.") # Adds the required 'path' argument for the file or repo.
    args = parser.parse_args() # Parses the command-line arguments provided by the user.

    output_dir = os.environ.get("THUTORPY_OUTPUT_DIR") # Retrieves the output directory path from the environment variables.
    if not output_dir: # Checks if the output directory environment variable was not set.
        print("Error: Output directory not configured. Please run 'source configure.sh' first.", file=sys.stderr) # Prints an error if the output directory is not configured.
        sys.exit(1) # Exits the script with an error code.

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # Gets the current date and time to create a unique folder name.
    sanitized_path = os.path.basename(args.path).replace('.git', '') # Cleans up the input path to use as part of the folder name.
    execution_dir_name = f"{timestamp}_{sanitized_path}" # Combines the timestamp and sanitized path for the final directory name.
    execution_dir = os.path.join(output_dir, execution_dir_name) # Creates the full path for the new execution-specific output directory.
    
    os.makedirs(execution_dir, exist_ok=True) # Creates the unique output directory.
    abs_execution_dir = os.path.abspath(execution_dir) # Gets the absolute path of the output directory for a clean display.
    print(f"Output will be saved to: {abs_execution_dir}") # Informs the user where the output files will be saved.

    if is_git_repo(args.path): # Checks if the user provided a GitHub repository URL.
        process_repository(args.path, execution_dir) # Calls the function to process the repository.
    elif os.path.isfile(args.path): # Checks if the user provided a path to a local file.
        process_file(args.path, execution_dir) # Calls the function to process the single file.
    else: # Handles cases where the input is neither a valid file nor a GitHub URL.
        print(f"Error: The path '{args.path}' is not a valid file or GitHub repository URL.", file=sys.stderr) # Prints an error message for invalid input.
        sys.exit(1) # Exits the script with an error code.

    # --- Final User Message --- # A separator comment for the final user message block.
    print("\n" + "="*50) # Prints a newline and a separator line for visual clarity.
    print("✅ Analysis complete!") # Prints a success message to the user.
    print(f"Commented files are saved in: {abs_execution_dir}") # Shows the final location of the output files.
    print("To navigate to the output directory, you can run:") # Provides instructions on how to get to the files.
    print(f"cd {abs_execution_dir}") # Prints the exact 'cd' command for the user to copy.
    print("="*50 + "\n") # Prints another separator line and a final newline.


if __name__ == "__main__": # Checks if this script is being run directly (not imported).
    main() # Calls the main function to start the program.