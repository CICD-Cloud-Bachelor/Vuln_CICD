#!/bin/bash

# Update and install required packages
sudo apt update
sudo apt install docker-compose git curl python3.10-venv whiptail -y

# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

echo "#######################################################"
echo "#                   LOGIN TO AZURE                    #"
echo "#######################################################"
az login --use-device-code

# Use whiptail to interactively ask for PAT and Organization Name
PAT=$(whiptail --inputbox "Enter your Azure DevOps Personal Access Token:" 8 78 --title "Personal Access Token Input" 3>&1 1>&2 2>&3)
ORGANIZATION_NAME=$(whiptail --inputbox "Enter your Azure DevOps Organization Name:" 8 78 --title "Organization Name Input" 3>&1 1>&2 2>&3)

# Check if the user cancelled the input
if [ $? -eq 1 ]; then
    echo "User cancelled the input. Exiting..."
    exit 1
fi

# Install Pulumi
curl -fsSL https://get.pulumi.com | sh
export PATH=$PATH:$HOME/.pulumi/bin
lines_to_add="export PATH=\$PATH:\$HOME/.pulumi/bin"
# Detect the current shell using the SHELL variable and append to the appropriate rc file
case $SHELL in
    */bash)
        echo "$lines_to_add" >> ~/.bashrc
        echo "Lines added to .bashrc successfully."
        ;;
    */zsh)
        echo "$lines_to_add" >> ~/.zshrc
        echo "Lines added to .zshrc successfully."
        ;;
    */ksh)
        echo "$lines_to_add" >> ~/.kshrc
        echo "Lines added to .kshrc successfully."
        ;;
    # Add more cases as needed for different shells
    *)
        echo "Unsupported shell: $SHELL"
        ;;
esac

# Clone the repository and generate a Pulumi project
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
