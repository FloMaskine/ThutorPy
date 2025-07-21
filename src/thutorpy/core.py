import os
import requests
import json
import sys

def generate_comment_with_ollama(code_line, entire_code, ollama_api_url, ollama_model):
    """
    Generates a comment for a line of code using Ollama, with the entire code for context.
    """
    prompt = (
        "You are an expert code commenter. Explain the following single line of code "
        "in a concise, one-sentence comment. Do not output anything else, just the comment text.\n\n"
        f"The full code context is:\n```\n{entire_code}\n```\n\n"
        f"The line to comment on is: \"{code_line}\""
    )
    
    try:
        response = requests.post(
            ollama_api_url,
            json={"model": ollama_model, "prompt": prompt, "stream": False},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        response_json = response.json()
        comment = response_json.get("response", "Could not get a comment.").strip()
        return comment.replace('"', '').replace("'", "")

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama: {e}", file=sys.stderr)
        return "Ollama connection error"

def analyze_code(file_path, output_path, config):
    """
    Analyzes the code in the given file and adds comments line by line,
    saving the output to the specified output_path.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        lines = code.splitlines()
        
        new_lines = []
        for line in lines:
            if line.strip():
                comment = generate_comment_with_ollama(
                    line.strip(), 
                    code, 
                    config['OLLAMA_API_URL'], 
                    config['OLLAMA_MODEL']
                )
                new_lines.append(f"{line}  # {comment}")
            else:
                new_lines.append(line)
                
        commented_code = "\n".join(new_lines)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(commented_code)
        
        return commented_code

    except (UnicodeDecodeError, IsADirectoryError):
        print(f"Skipping file (not a text file): {file_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error analyzing file {file_path}: {e}", file=sys.stderr)
        return None