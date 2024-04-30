# Vuln_CICD


## Azure Setup
### Create a DevOps Organization
Create a DevOps organization using the on the following URL: https://aex.dev.azure.com 



## Install

### Using Docker
By using Docker, the environment will be setup inside of a container and will not interfere with the host system. This is an easy an reliable way to start the application. 
Use the following commands to build and run the Docker container.
```
docker build -t pulumicicddocker .
docker run -it pulumicicddocker /bin/bash
```
Inside the container you need to login to Azure using the Azure CLI tool: `az`. Enter the following command:
```
az login --use-device-code
```
This will prompt you to access a link in the web browser and use a one-time-code to verify the login. Then choose your Azure account for which to use for this application.

After this has completed, the environment is ready.

Run `pulumi up` to start the application.


### Manual
```
sudo apt update
sudo apt install git curl python3 python3-pip python3.10-venv -y

git clone https://github.com/CICD-Cloud-Bachelor/Vuln_CICD.git
cd Vuln_CICD

curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az login --use-device-code

curl -fsSL https://get.pulumi.com | sh
export PATH=$PATH:$HOME/.pulumi/bin

python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

pulumi login
pulumi stack init dev
pulumi stack select dev
pulumi config set azure-native:location westeurope
pulumi config set azuredevops:personalAccessToken $PAT --plaintext
pulumi config set azuredevops:orgServiceUrl https://dev.azure.com/$ORGANIZATION_NAME
```

## Configure `az` cli
```
az login --use-device-code
```

# Configuration Details for `config.ini`

The `config.ini` file serves as the central configuration hub for the project, encompassing critical settings that are essential for the correct functioning of the application within Azure, GitHub, and Docker environments. This file includes credentials, resource names, and specific paths that are utilized across various services. Here is an explanation of each section and its parameters:

## [AZURE]
- **DOMAIN**: Specifies the unique domain for the Azure Active Directory tenant, e.g., `bacheloroppgave2024proton.onmicrosoft.com`.
- **USERNAME**: The username associated with the Azure account, e.g., `bachelor_oppgave2024`.
- **ORGANIZATION_NAME**: The name of the Azure DevOps organization, e.g., `bachelor2024`.
- **PAT (Personal Access Token)**: A security token that enables access to the Azure DevOps services programmatically.
- **LOCATION**: The Azure region where resources will be deployed, e.g., `westeurope`.
- **STORAGE_ACCOUNT_NAME**: 
  - Must be unique across all Azure accounts.
  - Should be between 3 and 24 characters, containing only lowercase letters and numbers.
  - 10 random hex digits are appended to ensure uniqueness.
  - The length in the `config.ini` file must therefore not be longer than 13 characters.
- **STORAGE_CONTAINER_NAME**:
  - Must follow the same uniqueness and character rules as `STORAGE_ACCOUNT_NAME`.

## [GITHUB]
- **PAT (Personal Access Token)**: Token used for authentication to GitHub to manage private repositories and other resources. Is only used if `is_private=True` is done in the `import_github_repo()` function.

## [DOCKER]
- **DNS_LABEL**: A unique DNS label for Docker-related resources.
  - 10 random hex digits are appended to ensure uniqueness.
- **REGISTRY_NAME**:
  - The name of the Docker registry.
  - Must not exceed 50 characters in length.
  - 10 random hex digits are appended to ensure uniqueness.
  - The length in the `config.ini` file must therefore not be longer than 39 characters.
- **CONTAINER_PATH**: The file path relative to the root project directory that leads to Docker configurations and images.

## General Guidelines for `config.ini`
- **Uniqueness**: Any parameter that specifies a resource name which must be globally or regionally unique will have a safeguard by appending random hex digits to prevent name collisions. This includes storage account names, container names, DNS labels, and registry names.
- **Security**: Sensitive information such as Personal Access Tokens (PAT) should be handled securely. Ensure that the `config.ini` file is not included in version control to prevent unauthorized access.
- **Validation**: When configuring the parameters, ensure that the values meet the required criteria for length and character set to avoid deployment issues.

This structured format aims to provide clear and concise information about each configuration parameter, ensuring that the setup process is as smooth as possible.

## Common Problems

Encountering issues during the setup or operation of the CI/CD pipeline can be frustrating. Below are solutions to some common problems that you might face when working with Azure DevOps.

### Can't Run Pipeline

**Issue**: When trying to run a pipeline, you encounter an error message indicating that no parallelism has been purchased or granted.

**Error Message**:
```
No hosted parallelism has been purchased or granted. To request a free parallelism grant, please fill out the following form https://aka.ms/azpipelines-parallelism-request
```

**Solution**: Azure DevOps requires parallelism, which refers to the number of concurrent jobs that can run. If your account does not have any parallel jobs available, you need to request them. This can be done for free for certain account types, particularly open-source projects or small teams.

- **Request Parallelism**: Fill out the [parallelism request form](https://aka.ms/azpipelines-parallelism-request) provided by Azure to apply for additional parallelism.

### Can't Add User in Azure DevOps

**Issue**: When attempting to add a new user to your Azure DevOps organization, especially a user from outside your Azure directory, you receive an error related to security settings.

**Error Message**:
```
Creating user entitlement: Adding user entitlement: (5101) You are trying to invite a user from outside your directory, but the security setting of this organization doesn't allow it.
```

**Solution**: This problem occurs because external guest access is disabled by default to protect your organization. You need to enable this setting to add external users.

- **Enable External Guest Access**:
  - Navigate to your Azure DevOps portal.
  - Go to `Organization Settings` -> `Security` -> `Policies`.
  - Under `User Policies`, find and enable `External guest access`.

Enabling this setting will allow you to invite and collaborate with users who are not part of your Azure Active Directory domain, expanding your development team's capabilities.

### Azure DNS Lookup Error

**Issue**: In rare cases there may be a DNS lookup error to Azure. 

**Error Message**:
```
Options "https://dev.azure.com/ORG/_apis": dial tcp: lookup dev.azure.com on 172.28.240.1:53: read udp 172.28.243.145:35138->172.28.240.1:53: i/o timeout
```

**Solution**: Run `pulumi up` again