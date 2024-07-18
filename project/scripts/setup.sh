#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for pipx and install if not present
if ! command_exists pipx; then
    echo "pipx is not installed. Installing pipx..."
    pip install pipx
    if [ $? -ne 0 ]; then
        echo "Failed to install pipx. Exiting."
        exit 1
    fi
    echo "Ensuring pipx path is added to PATH..."
    pipx ensurepath
    # Reload the shell configuration to include pipx in PATH
    if [ -f "$HOME/.bashrc" ]; then
        source "$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        source "$HOME/.bash_profile"
    elif [ -f "$HOME/.zshrc" ]; then
        source "$HOME/.zshrc"
    fi
else
    echo "pipx is already installed."
fi

# Check for poetry and install if not present
if ! command_exists poetry; then
    echo "poetry is not installed. Installing poetry using pipx..."
    pipx install poetry
    if [ $? -ne 0 ]; then
        echo "Failed to install poetry. Exiting."
        exit 1
    fi
else
    echo "poetry is already installed."
fi

# Configure poetry to create virtual environments in the project directory
echo "Configuring poetry for the \`backend\` directory..."
cd backend/
poetry config virtualenvs.in-project true

# Install project dependencies using poetry
echo "Installing project dependencies with poetry..."
poetry install
if [ $? -ne 0 ]; then
    echo "Failed to install project dependencies with poetry. Exiting."
    exit 1
fi

# Install pre-commit hooks using poetry
# echo "Installing pre-commit hooks with poetry..."
# poetry run pre-commit install
# if [ $? -ne 0 ]; then
#     echo "Failed to install pre-commit hooks with poetry. Exiting."
#     exit 1
# fi

echo "Environment setup completed successfully."
