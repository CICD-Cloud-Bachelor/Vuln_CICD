# Vuln_CICD

## Install

```
git clone https://github.com/CICD-Cloud-Bachelor/Vuln_CICD.git .
pulumi new python --name "mypulumiproject" --generate-only --force
git restore .

python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

pulumi stack select dev
pulumi config set azure-native:location westeurope
pulumi config set azuredevops:personalAccessToken $PAT --plaintext
pulumi config set azuredevops:orgServiceUrl https://dev.azure.com/bachelorcicd2024
```



## Common problems

### Can't run pipeline
If no hosted parallelism has been granted or purchased beforehand you need to do so manually using this [form](https://aka.ms/azpipelines-parallelism-request)

This error is given in Azure DevOps when running a pipeline if no parallelism has been purchased or granted
```
No hosted parallelism has been purchased or granted. To request a free parallelism grant, please fill out the following form https://aka.ms/azpipelines-parallelism-request
```

### Can't add user in Azure DevOps
If you receive this error, then you need to enable external guest access in your Azure DevOps organization access.
```
Creating user entitlement: Adding user entitlement: (5101) You are trying to invite a user from outside your directory, but the security setting of this organization doesn't allow it.
```
Go to your organization, then enable external guest access likt this:
```
Organization Settings -> Security -> Policies -> User Policies -> External guest access
```