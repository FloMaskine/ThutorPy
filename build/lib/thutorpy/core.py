import os # Imports the library for interacting with the operating system, used here for environment variables.
import requests # Imports the library for making HTTP requests to the Ollama API.
import json # Imports the library for working with JSON data, though not explicitly used in the final version.
import sys # Imports the library for system-specific parameters and functions, used here for printing to stderr.

def generate_comment_with_ollama(code_line, entire_code): # Defines the function that communicates with the Ollama API.
    """ # Starts a multi-line docstring to explain the function's purpose.
    Generates a comment for a line of code using Ollama, with the entire code for context. # Explains what the function does.
    """ # Ends the multi-line docstring.
    ollama_api_url = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate") # Gets the Ollama API URL from environment variables, with a default value.
    ollama_model = os.environ.get("OLLAMA_MODEL", "llama3") # Gets the desired Ollama model name from environment variables, with a default value.
    
    prompt = ( # Begins defining the multi-line prompt string that will be sent to the AI model.
        "You are an expert code commenter. Explain the following single line of code " # Sets the context and role for the AI.
        "in a concise, one-sentence comment. Do not output anything else, just the comment text.\n\n" # Provides strict instructions on the desired output format.
        f"The full code context is:\n```\n{entire_code}\n```\n\n" # Includes the entire file's code to give the AI context.
        f"The line to comment on is: \"{code_line}\"" # Specifies the exact line of code that needs a comment.
    ) # Ends the multi-line prompt string definition.
    
    try: # Starts a block to handle potential errors during the API request.
        response = requests.post( # Sends an HTTP POST request to the Ollama API.
            ollama_api_url, # The URL of the Ollama API endpoint.
            json={"model": ollama_model, "prompt": prompt, "stream": False}, # The data payload, including the model, prompt, and non-streaming option.
            headers={"Content-Type": "application/json"} # Sets the HTTP header to indicate the content is JSON.
        ) # Finishes the requests.post call.
        response.raise_for_status() # Checks if the HTTP request returned an error status code (like 404 or 500).
        
        response_json = response.json() # Parses the JSON response from the API into a Python dictionary.
        comment = response_json.get("response", "Could not get a comment.").strip() # Extracts the generated comment text, with a default error message.
        return comment.replace('"', '').replace("'", "") # Cleans up the comment by removing any quotes and returns it.

    except requests.exceptions.RequestException as e: # Catches any network-related errors during the request.
        # Print errors to stderr so they don't interfere with the clean output # A comment explaining why errors are sent to stderr.
        print(f"Error connecting to Ollama: {e}", file=sys.stderr) # Prints the connection error message to the standard error stream.
        return "Ollama connection error" # Returns a standard error message to be placed as a comment in the code.

def analyze_code(file_path, output_path): # Defines the main function for analyzing a single file.
    """ # Starts a multi-line docstring to explain the function's purpose.
    Analyzes the code in the given file and adds comments line by line, # Explains that the function analyzes and comments code.
    saving the output to the specified output_path. # Specifies that the result is saved to a file.
    """ # Ends the multi-line docstring.
    try: # Starts a block to handle potential errors during file processing.
        with open(file_path, 'r', encoding='utf-8') as f: # Opens the source file in read mode with UTF-8 encoding.
            code = f.read() # Reads the entire content of the file into the 'code' variable.
        lines = code.splitlines() # Splits the file content into a list of individual lines.
        
        new_lines = [] # Initializes an empty list to store the new lines with comments.
        for line in lines: # Starts a loop to iterate over each line of the original code.
            if line.strip(): # Checks if the line is not empty or just whitespace.
                comment = generate_comment_with_ollama(line.strip(), code) # Calls the Ollama function to get a comment for the current line.
                new_lines.append(f"{line}  # {comment}") # Appends the original line plus the new comment to the list.
            else: # Handles cases where the line is empty.
                new_lines.append(line) # Appends the empty line to the list without adding a comment.
                
        commented_code = "\n".join(new_lines) # Joins all the new lines back together into a single string.
        
        with open(output_path, 'w', encoding='utf-8') as f: # Opens the destination file in write mode with UTF-8 encoding.
            f.write(commented_code) # Writes the fully commented code to the output file.
        
        return commented_code # Returns the commented code as a string.

    except (UnicodeDecodeError, IsADirectoryError): # Catches errors for non-text files or directories.
        print(f"Skipping file (not a text file): {file_path}", file=sys.stderr) # Prints a message to stderr that the file is being skipped.
        return None # Returns None to indicate that the analysis failed for this file.
    except Exception as e: # Catches any other general exceptions during the process.
        print(f"Error analyzing file {file_path}: {e}", file=sys.stderr) # Prints a generic error message to stderr.
        return None # Returns None to indicate that the analysis failed.
