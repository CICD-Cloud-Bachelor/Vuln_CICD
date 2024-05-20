FROM ubuntu:22.04


########################################################################
#   CHANGE THE ENVIRONMENT VARIABLES BELOW TO MATCH YOUR OWN SETTINGS  #
########################################################################
ENV PULUMI_ACCESS_TOKEN=""
ENV DEVOPS_PAT=""
ENV DOMAIN=""
ENV USERNAME=""
ENV ORGANIZATION_NAME=""
ENV AZURE_TENANT_ID=""
#######################################################################
#                   OPTIONAL ENVIRONMENT VARIABLES                    #
#######################################################################
ENV LOCATION="westeurope"
ENV STORAGE_ACCOUNT_NAME="storaccount"
ENV STORAGE_CONTAINER_NAME="storcontainer"
ENV GITHUB_PAT="NULL"
ENV DNS_LABEL="pulumibachelorproject"
ENV REGISTRY_NAME="registrypulumi"
#######################################################################

WORKDIR /app
COPY . .
ENV PATH="/root/.pulumi/bin:${PATH}"
ENV PYTHONDONTWRITEBYTECODE=1

RUN --mount=type=cache,target=/var/cache/apt \
    apt update && \
    apt install -y curl python3-venv python3-pip && \
    curl -sL https://aka.ms/InstallAzureCLIDeb | bash && \
    curl -fsSL https://get.pulumi.com | sh && \
    python3 -m venv venv && \
    . venv/bin/activate && \
    python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install -r requirements.txt && \
    pulumi login && \
    stack_name="dev"$(cat /dev/urandom | tr -dc A-Za-z0-9_ | head -c 10) && \
    pulumi stack init "${stack_name}" && \
    pulumi stack select "${stack_name}" && \
    pulumi config set azuredevops:personalAccessToken "${DEVOPS_PAT}" --plaintext && \
    pulumi config set azuredevops:orgServiceUrl "https://dev.azure.com/${ORGANIZATION_NAME}" && \ 
    pulumi refresh -y

CMD az login --tenant "${AZURE_TENANT_ID}" --use-device-code && exec bash
