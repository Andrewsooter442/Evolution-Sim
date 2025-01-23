#!/bin/bash

# Define project variables
REPO_URL="https://github.com/Andrewsooter442/Evolution-Sim.git"
PROJECT_DIR="Evolution-Sim"
ENV_NAME="Evolution-Sim"
PYTHON_VERSION="3.13"

echo "Cloning repository..."
git clone "$REPO_URL"

cd "$PROJECT_DIR" || { echo "Failed to enter project directory"; exit 1; }
echo "cd into the $(pwd) directory"

if command -v conda &> /dev/null; then
    echo "Conda is available. Setting up a Conda environment."
    conda create -y -n "$ENV_NAME" python="$PYTHON_VERSION"
    
    # Initialize Conda if not done
    conda init
    
    # Activate the environment
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate "$ENV_NAME"
    echo "Created the conda environment successfully"
else
    echo "Conda is not available. We recommend using Conda for better dependency management."
    echo "Falling back to python -m venv."
    python3 -m venv "$ENV_NAME"
    source "$ENV_NAME/bin/activate"
fi

echo "Installing project dependencies..."
if [[ -f "environment.yml" && $(command -v conda) ]]; then
    conda env update -f environment.yml
elif [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
else
    echo "No environment.yml or requirements.txt found."
fi

cd Scripts
echo "Running the program..."
python main.py

echo "Setup complete. Exiting."

