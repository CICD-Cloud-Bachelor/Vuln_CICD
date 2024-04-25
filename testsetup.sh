#!/bin/bash

sudo apt update
sudo apt install curl python3.10-venv whiptail -y

# Check if config.ini exists
if [ -f config.ini ]; then
    whiptail --title "Error" --msgbox "You already have configured the environment with a config.ini file. Please remove it and run the script again." 10 60
    exit 1
fi

# Update and install required packages, using whiptail for progress
{
    echo 20
    sudo apt update
    echo 40
    sudo apt install curl python3.10-venv whiptail -y
    echo 60
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    echo 80
    az login --use-device-code
    echo 100
} | whiptail --gauge "Installing required packages and logging in to Azure..." 6 60 0

# Configuration inputs with whiptail
PAT=$(whiptail --inputbox "Enter your Azure DevOps Personal Access Token:" 8 78 --title "Personal Access Token Input" 3>&1 1>&2 2>&3)
ORGANIZATION_NAME=$(whiptail --inputbox "Enter your Azure DevOps Organization Name:" 8 78 --title "Organization Name Input" 3>&1 1>&2 2>&3)
DOMAIN=$(whiptail --inputbox "Enter your Azure Domain (ex: bacheloroppgave2024proton.onmicrosoft.com):" 8 78 --title "Domain Input" 3>&1 1>&2 2>&3)
USERNAME=$(whiptail --inputbox "Enter your Azure Username:" 8 78 --title "Username Input" 3>&1 1>&2 2>&3)
LOCATION=$(whiptail --inputbox "Enter your Azure Location (default: westeurope):" 8 78 --title "Location Input" 3>&1 1>&2 2>&3)
GITHUB_PAT=$(whiptail --inputbox "Enter your GitHub PAT:" 8 78 --title "GitHub PAT Input" 3>&1 1>&2 2>&3)
DNS_LABEL=$(whiptail --inputbox "Create a DNS Label for public access to containers (default: pulumibachelorproject):" 8 78 --title "DNS Label Input" 3>&1 1>&2 2>&3)

# Default values for those not given by the user
[ -z "$LOCATION" ] && LOCATION="westeurope"
[ -z "$GITHUB_PAT" ] && GITHUB_PAT="NULL"
[ -z "$DNS_LABEL" ] && DNS_LABEL="pulumibachelorproject"

# Create config.ini file
cat > config.ini << EOF
[AZURE]
DOMAIN = $DOMAIN
USERNAME = $USERNAME
ORGANIZATION_NAME = $ORGANIZATION_NAME
PAT = $PAT
LOCATION = $LOCATION
STORAGE_ACCOUNT_NAME = storaccount
STORAGE_CONTAINER_NAME = storcontainer

[GITHUB]
PAT = $GITHUB_PAT

[DOCKER]
DNS_LABEL = $DNS_LABEL
REGISTRY_NAME = registrypulumi
CONTAINER_PATH = source/docker_images/
EOF

whiptail --title "Configuration" --msgbox "config.ini has been created successfully." 8 78

# Install Pulumi
{
    curl -fsSL https://get.pulumi.com | sh
    echo "export PATH=\$PATH:\$HOME/.pulumi/bin" >> ~/.bashrc
    source ~/.bashrc
    echo 100
} | whiptail --gauge "Installing Pulumi..." 6 50 0

# Pulumi setup
pulumi new python --name "mypulumiproject" --generate-only --force -y
pulumi login
pulumi stack select dev

# Set configuration values in Pulumi
pulumi config set azure-native:location westeurope
pulumi config set azuredevops:personalAccessToken $PAT --plaintext
pulumi config set azuredevops:orgServiceUrl "https://dev.azure.com/$ORGANIZATION_NAME"

whiptail --title "Setup Complete" --msgbox "Setup completed successfully.\nPlease source your rc file to apply changes:\nsource ~/.bashrc\nYou can now run 'pulumi up' to deploy the infrastructure." 12 78
