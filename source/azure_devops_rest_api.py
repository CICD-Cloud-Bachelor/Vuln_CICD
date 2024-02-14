import pulumi
from pulumi.dynamic import Resource, ResourceProvider, CreateResult
import requests

class HttpPostProvider(ResourceProvider):
    def create(
            self, 
            inputs: dict
        ) -> CreateResult:

        response = requests.post(
            url=inputs['url'], 
            headers=inputs['headers'], 
            json=inputs['json'], 
            auth=tuple(inputs['auth'])
        )

        pulumi.log.info(f"HTTP request response: {response.text}")
        
        return CreateResult(id_="1", outs={"response": response.text})

class HttpPostResource(Resource):
    def __init__(
            self, 
            name: str, 
            url: str, 
            headers: dict, 
            json: list, 
            auth: str, 
            opts=None
        ) -> None:

        super().__init__(
            provider=HttpPostProvider(), 
            name=name, 
            props={
                "url": url,
                "headers": headers,
                "json": json,
                "auth": auth,
            }, 
            opts=opts
        )

class AzureDevOpsPipelineRunProvider(ResourceProvider):
    def create(self, props):
        url = f"https://dev.azure.com/{props['organization']}/{props['project']}/_apis/pipelines/{props['pipeline_id']}/runs?api-version=6"
        headers = {"Content-Type": "application/json"}
        json = {
            "resources": 
            {
                "repositories": 
                {
                    "self": 
                    {
                        "refName": f"refs/heads/{props['source_branch']}"
                    }
                }
            }
        }
        auth = (props["username"], props["personal_access_token"])

        response = requests.post(url, headers=headers, json=json, auth=auth)
        pulumi.log.info(f"Pipeline run created: {response.status_code}")
        return CreateResult(id_="1", outs={"response": response.text})

class AzureDevOpsPipelineRun(Resource):
    def __init__(
            self, 
            name, 
            organization, 
            project, 
            username, 
            personal_access_token, 
            pipeline_id, 
            source_branch,
            opts=None
        ) -> None:
        super().__init__(
            provider=AzureDevOpsPipelineRunProvider(), 
            name=name, 
            props={
                "organization": organization,
                "project": project,
                "username": username,
                "personal_access_token": personal_access_token,
                "pipeline_id": pipeline_id,
                "source_branch": source_branch,
            },
            opts=opts
        )