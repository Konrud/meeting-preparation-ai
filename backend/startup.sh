#!/bin/bash

# Check if running on Azure Web App
if [ -z "$WEBSITE_SITE_NAME" ]; then
  echo "IPE: startup.sh: Not running on Azure Web App. Skipping antenv creation and dependency installation."
  # Exit without installing dependencies
  exit 0
fi

# Commands that run only on Azure
echo "IPE: startup.sh: Running on Azure Web App. Setting up the environment..."

cd /home/site/wwwroot

# Check if the virtual environment "antenv" exists
if [ ! -d "antenv" ]; then
  echo "IPE: startup.sh: Creating virtual environment 'antenv'..."
  # Create a virtual environment named "antenv"
  python3 -m venv antenv
fi

echo "IPE: startup.sh: Activating the virtual environment..."
# Activate the virtual environment
source antenv/bin/activate

echo "IPE: startup.sh: Upgrading pip..."
# Upgrade pip and install dependencies
pip install --upgrade pip

echo "IPE: startup.sh: Installing dependencies from the requirements.txt file..."
# Install dependencies from the requirements.txt file
pip install -r requirements.txt

exec gunicorn src.main:app --config gunicorn_conf.py