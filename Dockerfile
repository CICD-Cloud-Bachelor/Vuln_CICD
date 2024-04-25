FROM ubuntu:latest

ENV PULUMI_ACCESS_TOKEN="pul-fb262df9bf3a794b7855469a1b7af23964958922"
ENV LOCATION="westeurope"
ENV DEVOPS_PAT="7mxuikujt3lg4tm5xbiexh3h5md7y664mzgi76cdwkmjm7rgtybq"
ENV DOMAIN="bacheloroppgave2024proton.onmicrosoft.com"
ENV USERNAME="bachelor_oppgave2024"
ENV ORGANIZATION_NAME="bachelor2024"
ENV STORAGE_ACCOUNT_NAME="storaccount"
ENV STORAGE_CONTAINER_NAME="storcontainer"
ENV GITHUB_PAT="NULL"
ENV DNS_LABEL="pulumibachelorproject"
ENV REGISTRY_NAME="registrypulumi"
ENV CONTAINER_PATH="source/docker_images/"

WORKDIR /app

RUN apt update && \
    apt install -y git curl python3 python3-pip python3.10-venv && \
    curl -sL https://aka.ms/InstallAzureCLIDeb | bash && \
    az login --use-device-code && \
    curl -fsSL https://get.pulumi.com | sh

ENV PATH="/root/.pulumi/bin:${PATH}"

RUN git clone https://matamel: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@github.com/CICD-Cloud-Bachelor/Vuln_CICD.git . && \
    git checkout Mathias

RUN pulumi new python --name "mypulumiproject" --generate-only --force -y && \
    git restore . && \
    python3 -m venv venv && \
    . venv/bin/activate && \
    python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install -r requirements.txt && \
    pulumi login && \
    pulumi stack select dev && \
    pulumi config set azure-native:location ${LOCATION} && \
    pulumi config set azuredevops:personalAccessToken ${DEVOPS_PAT} --plaintext && \
    pulumi config set azuredevops:orgServiceUrl "https://dev.azure.com/${ORGANIZATION_NAME}"

RUN printf "[AZURE]\nDOMAIN = %s\nUSERNAME = %s\nORGANIZATION_NAME = %s\nPAT = %s\nLOCATION = %s\nSTORAGE_ACCOUNT_NAME = %s\nSTORAGE_CONTAINER_NAME = %s\n\n[GITHUB]\nPAT = %s\n\n[DOCKER]\nDNS_LABEL = %s\nREGISTRY_NAME = %s\nCONTAINER_PATH = %s\n" \
"$DOMAIN" "$USERNAME" "$ORGANIZATION_NAME" "$DEVOPS_PAT" "$LOCATION" "$STORAGE_ACCOUNT_NAME" "$STORAGE_CONTAINER_NAME" "$GITHUB_PAT" "$DNS_LABEL" "$REGISTRY_NAME" "$CONTAINER_PATH" > config.ini

ENTRYPOINT [ "/bin/bash" ]