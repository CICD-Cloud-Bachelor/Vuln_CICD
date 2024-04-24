#!/bin/bash

if [ -f config.ini ]; then
    echo "You already have configured the environment with a config.ini file. Please remove it and run the script again."
    exit 1
fi

# Update and install required packages
sudo apt update
sudo apt install docker-compose git curl python3.10-venv whiptail -y

# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

echo "#######################################################"
echo "#                   LOGIN TO AZURE                    #"
echo "#######################################################"
az login --use-device-code

# Requesting user inputs with whiptail
PAT=$(whiptail --inputbox "Enter your Azure DevOps Personal Access Token:" 8 78 --title "Personal Access Token Input" 3>&1 1>&2 2>&3)
ORGANIZATION_NAME=$(whiptail --inputbox "Enter your Azure DevOps Organization Name:" 8 78 --title "Organization Name Input" 3>&1 1>&2 2>&3)
DOMAIN=$(whiptail --inputbox "Enter your Azure Domain (ex: bacheloroppgave2024proton.onmicrosoft.com):" 8 78 --title "Domain Input" 3>&1 1>&2 2>&3)
USERNAME=$(whiptail --inputbox "Enter your Azure Username:" 8 78 --title "Username Input" 3>&1 1>&2 2>&3)

# Allow users to skip input for LOCATION and use default if they do
LOCATION=$(whiptail --inputbox "Enter your Azure Location (default: westeurope):" 8 78 --title "Location Input" 3>&1 1>&2 2>&3)
if [ -z "$LOCATION" ]; then
    LOCATION="westeurope"
fi

GITHUB_PAT=$(whiptail --inputbox "Enter your GitHub PAT:" 8 78 --title "GitHub PAT Input" 3>&1 1>&2 2>&3)

# Allow users to skip input for DNS_LABEL and use default if they do
DNS_LABEL=$(whiptail --inputbox "Create a DNS Label for public access to containers (default: pulumibachelorproject):" 8 78 --title "DNS Label Input" 3>&1 1>&2 2>&3)
if [ -z "$DNS_LABEL" ]; then
    DNS_LABEL="pulumibachelorproject"
fi

# Default values for those not given by the user
STORAGE_ACCOUNT_NAME="storaccount"
STORAGE_CONTAINER_NAME="storcontainer"
REGISTRY_NAME="registrypulumi"
CONTAINER_PATH="source/docker_images/"

# Create config.ini file
cat > config.ini << EOF
[AZURE]
DOMAIN = $DOMAIN
USERNAME = $USERNAME
ORGANIZATION_NAME = $ORGANIZATION_NAME
PAT = $PAT
LOCATION = $LOCATION
STORAGE_ACCOUNT_NAME = $STORAGE_ACCOUNT_NAME
STORAGE_CONTAINER_NAME = $STORAGE_CONTAINER_NAME

[GITHUB]
PAT = $GITHUB_PAT

[DOCKER]
DNS_LABEL = $DNS_LABEL
REGISTRY_NAME = $REGISTRY_NAME
CONTAINER_PATH = $CONTAINER_PATH
EOF

echo "config.ini has been created successfully."

# Check if the user cancelled the input
if [ $? -eq 1 ]; then
    echo "User cancelled the input. Exiting..."
    exit 1
fi

# Install Pulumi
curl -fsSL https://get.pulumi.com | sh
echo "export PATH=\$PATH:\$HOME/.pulumi/bin" >> ~/.bashrc
source ~/.bashrc

# Clone the repository and generate a Pulumi project
pulumi new python --name "mypulumiproject" --generate-only --force -y
git restore .

# Setup Python virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

# Log into Pulumi
echo "#######################################################"
echo "#                   LOGIN TO PULUMI                   #"
echo "#######################################################"
pulumi login

# Initialize and select Pulumi stack
#pulumi stack init dev
pulumi stack select dev


# Set configuration values in Pulumi
pulumi config set azure-native:location westeurope
pulumi config set azuredevops:personalAccessToken $PAT --plaintext
pulumi config set azuredevops:orgServiceUrl "https://dev.azure.com/$ORGANIZATION_NAME"


echo "#######################################################"
echo "#                 SETUP COMPLETED                     #"
echo "#######################################################"
echo "Please source your rc file to apply changes:"
echo "source ~/.bashrc"