#!/bin/bash

# Update and install required packages
sudo apt update
sudo apt install docker-compose git curl python3.10-venv whiptail -y

# Use whiptail to interactively ask for PAT and Organization Name
PAT=$(whiptail --inputbox "Enter your Azure DevOps Personal Access Token:" 8 78 --title "Personal Access Token Input" 3>&1 1>&2 2>&3)
ORGANIZATION_NAME=$(whiptail --inputbox "Enter your Azure DevOps Organization Name:" 8 78 --title "Organization Name Input" 3>&1 1>&2 2>&3)

# Check if the user cancelled the input
if [ $? -eq 1 ]; then
    echo "User cancelled the input. Exiting..."
    exit 1
fi
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az login --use-device-code

# Install Pulumi
curl -fsSL https://get.pulumi.com | sh
export PATH=$PATH:$HOME/.pulumi/bin

# Clone the repository and generate a Pulumi project
git clone https://github.com/CICD-Cloud-Bachelor/Vuln_CICD.git .
pulumi new python --name "mypulumiproject" --generate-only --force
git restore .

# Setup Python virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

# Log into Pulumi
pulumi login

# Initialize and select Pulumi stack
pulumi stack init dev
pulumi stack select dev


# Set configuration values in Pulumi
pulumi config set azure-native:location westeurope
pulumi config set azuredevops:personalAccessToken $PAT --plaintext
pulumi config set azuredevops:orgServiceUrl "https://dev.azure.com/$ORGANIZATION_NAME"

echo "Setup complete. Please verify everything is configured correctly."
