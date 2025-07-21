import os
import sys
import json
import subprocess
import time

CONFIG_PATH = os.path.expanduser("~/.thutorpy_config.json")

def is_interactive():
    """Check if the script is running in an interactive terminal."""
    return sys.stdout.isatty()

def configure():
    """Interactive configuration script for ThutorPy."""
    if not is_interactive():
        print("Error: This configuration script must be run in an interactive terminal.", file=sys.stderr)
        sys.exit(1)

    print("--- ThutorPy Configuration ---")
    
    config = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)

    # 1. Check for Ollama installation
    try:
        subprocess.run(['ollama', '--version'], check=True, capture_output=True)
    except FileNotFoundError:
        print("Ollama is not installed.")
        install_choice = input("Do you want to install Ollama now? (y/n): ").lower().strip()
        if install_choice == 'y':
            print("Installing Ollama...")
            try:
                install_command = "curl -fsSL https://ollama.com/install.sh | sh"
                subprocess.run(install_command, shell=True, check=True)
                print("Ollama installed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Ollama installation failed: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("Please install Ollama manually and run 'thutorpy-configure' again.", file=sys.stderr)
            sys.exit(1)

    # 2. Check if Ollama server is running
    try:
        subprocess.run(['ollama', 'list'], check=True, capture_output=True, text=True)
        print("Ollama server is running.")
    except subprocess.CalledProcessError:
        print("Ollama server is not running.")
        start_choice = input("Do you want to start the Ollama server now? (y/n): ").lower().strip()
        if start_choice == 'y':
            print("Starting Ollama server in the background...")
            subprocess.Popen(['ollama', 'serve'])
            print("Giving the server a moment to start...")
            time.sleep(5)
            try:
                subprocess.run(['ollama', 'list'], check=True, capture_output=True)
                print("Ollama server started successfully.")
            except (FileNotFoundError, subprocess.CalledProcessError):
                print("Failed to start Ollama server. Please start it manually.", file=sys.stderr)
                sys.exit(1)
        else:
            print("Please start the Ollama server and run 'thutorpy-configure' again.", file=sys.stderr)
            sys.exit(1)

    # 3. Set API URL
    default_api_url = config.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
    api_url = input(f"Enter the Ollama API URL [default: {default_api_url}]: ").strip()
    if not api_url:
        api_url = default_api_url

    # 4. Set Output Directory
    default_output_dir = config.get("THUTORPY_OUTPUT_DIR", os.path.join(os.path.expanduser("~"), "thutorpy_output"))
    output_dir = input(f"Enter the base directory for output files [default: {default_output_dir}]: ").strip()
    if not output_dir:
        output_dir = default_output_dir
    os.makedirs(output_dir, exist_ok=True)

    # 5. Set Model
    print("\nFetching available Ollama models...")
    models_raw = subprocess.run(['ollama', 'list'], check=True, capture_output=True, text=True).stdout
    models = [line.split()[0] for line in models_raw.strip().split('\n')[1:]]
    
    print("Please choose a model to use:")
    for i, model in enumerate(models):
        print(f"  {i+1}) {model}")
    
    while True:
        try:
            model_num = int(input("Enter the number of the model you want to use: "))
            if 1 <= model_num <= len(models):
                selected_model = models[model_num - 1]
                break
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # 6. Save configuration
    new_config = {
        "OLLAMA_API_URL": api_url,
        "THUTORPY_OUTPUT_DIR": output_dir,
        "OLLAMA_MODEL": selected_model
    }

    with open(CONFIG_PATH, 'w') as f:
        json.dump(new_config, f, indent=4)

    print("\n" + "="*50)
    print("✅ Configuration saved successfully!")
    print(f"Settings saved to: {CONFIG_PATH}")
    print("="*50 + "\n")

def load_config():
    """Loads the configuration from the config file."""
    if not os.path.exists(CONFIG_PATH):
        print("Error: ThutorPy is not configured. Please run 'thutorpy-configure' first.", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)