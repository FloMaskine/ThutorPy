#!/bin/bash
# This script configures the environment variables for ThutorPy.
# To apply these settings, run this script using the 'source' command:
# source configure.sh

# --- Ollama Installation Check ---
if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed."
    echo "This script can attempt to install it for you."
    read -p "Do you want to install Ollama now? (y/n): " install_choice
    if [[ "$install_choice" == "y" || "$install_choice" == "Y" ]]; then
        echo "Installing Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
        if [ $? -ne 0 ]; then
            echo "Ollama installation failed. Please install it manually and run this script again."
            return 1
        fi
        echo "Ollama installed successfully."
    else
        echo "Please install Ollama manually and run this script again."
        return 1
    fi
fi

# --- Ollama Server Check ---
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "Ollama server is not running. Starting it now in the background..."
    ollama serve &
    sleep 5
    echo "Ollama server started."
else
    echo "Ollama server is already running."
fi

# --- API URL Configuration ---
DEFAULT_API_URL="http://localhost:11434/api/generate"
echo -n "Enter the Ollama API URL [default: ${OLLAMA_API_URL:-$DEFAULT_API_URL}]: "
read user_api_url
export OLLAMA_API_URL=${user_api_url:-${OLLAMA_API_URL:-$DEFAULT_API_URL}}

# --- Model Selection ---
DEFAULT_MODEL="qwen2.5:3b"
use_default_model=false

echo "Fetching available Ollama models..."
mapfile -t models < <(ollama list | tail -n +2 | awk '{print $1}')

# Check if the default model is available
for model in "${models[@]}"; do
    if [[ "$model" == "$DEFAULT_MODEL" ]]; then
        use_default_model=true
        break
    fi
done

# If default model is not installed, ask to pull it
if [ "$use_default_model" = false ]; then
    echo "Default model '$DEFAULT_MODEL' is not installed."
    read -p "Do you want to pull it now? (y/n): " pull_choice
    if [[ "$pull_choice" == "y" || "$pull_choice" == "Y" ]]; then
        echo "Pulling '$DEFAULT_MODEL'... This may take a while."
        ollama pull "$DEFAULT_MODEL"
        if [ $? -eq 0 ]; then
            echo "'$DEFAULT_MODEL' pulled successfully."
            # Add the new model to the list
            models+=("$DEFAULT_MODEL")
            export OLLAMA_MODEL=$DEFAULT_MODEL
        else
            echo "Failed to pull '$DEFAULT_MODEL'."
        fi
    else
        echo "Skipping pull of default model."
    nfi
fi

# If a model is already set, ask to change it
if [ -n "$OLLAMA_MODEL" ]; then
    read -p "A model is already set to '$OLLAMA_MODEL'. Do you want to change it? (y/n): " change_model_choice
    if [[ "$change_model_choice" != "y" && "$change_model_choice" != "Y" ]]; then
        echo "Keeping the current model: $OLLAMA_MODEL"
    else
        # Unset the variable to trigger selection
        unset OLLAMA_MODEL
    fi
fi

# If no model is set, prompt for selection
if [ -z "$OLLAMA_MODEL" ]; then
    if [ ${#models[@]} -eq 0 ]; then
        echo -e "\nNo Ollama models are currently installed!"
        read -p "Please enter the name of a model to pull (e.g., llama3): " model_to_pull
        if [ -n "$model_to_pull" ]; then
            ollama pull "$model_to_pull"
            export OLLAMA_MODEL=$model_to_pull
        else
            echo "No model selected. Exiting."
            return 1
        fi
    else
        echo "Please choose a model to use:"
        for i in "${!models[@]}"; do
            echo "  $((i+1))) ${models[$i]}"
        done
        echo "  $((${#models[@]}+1))) Enter a different model name"
        
        while true; do
            read -p "Enter the number of your choice: " model_num
            if [[ "$model_num" -ge 1 && "$model_num" -le "${#models[@]}" ]]; then
                export OLLAMA_MODEL=${models[$((model_num-1))]}
                break
            elif [ "$model_num" -eq $((${#models[@]}+1)) ]; then
                read -p "Enter the name of the model you want to use: " custom_model
                export OLLAMA_MODEL=$custom_model
                break
            else
                echo "Invalid number. Please try again."
            fi
        done
    fi
fi

# --- Output Directory Configuration ---
echo -n "Enter the base directory for output files [default: ${THUTORPY_OUTPUT_DIR:-./thutorpy_output}]: "
read user_output_dir
export THUTORPY_OUTPUT_DIR=${user_output_dir:-${THUTORPY_OUTPUT_DIR:-./thutorpy_output}}
# Create the directory if it doesn't exist
mkdir -p "$THUTORPY_OUTPUT_DIR"

echo ""
echo "ThutorPy environment variables configured:"
echo "-----------------------------------------"
echo "OLLAMA_API_URL:      $OLLAMA_API_URL"
echo "OLLAMA_MODEL:        $OLLAMA_MODEL"
echo "THUTORPY_OUTPUT_DIR: $(realpath "$THUTORPY_OUTPUT_DIR")"
echo ""
echo "You can now run the 'thutorpy' tool in this terminal session."
