from pulumi.dynamic import ResourceProvider, Resource, CreateResult
import requests, pulumi, random
from faker import Faker


class HttpPostProvider(ResourceProvider):
    def create(self, inputs):
        response = requests.post(inputs['url'], headers=inputs['headers'], json=inputs['json'], auth=tuple(inputs['auth']))
        pulumi.log.info(f"HTTP request response: {response.text}")
        return CreateResult(id_="1", outs={"response": response.text})

class HttpPostResource(Resource):
    def __init__(self, name, url, headers, json, auth, opts=None):
        super().__init__(HttpPostProvider(), name, {
            "url": url,
            "headers": headers,
            "json": json,
            "auth": auth,
        }, opts)


class WorkItem:
    index = 0
    def __init__(self, project_name, depends_on):
        self.project_name = project_name
        self.auth = ("bachelor_oppgave2024", "hxjg7hxn4q4jitnoglqxlgw2lice6e2556u7ma6ulsxiizcqoiqa")
        self.headers = {"Content-Type": "application/json-patch+json"}
        self.depends_on = depends_on

    def create(self, type, title, description, comment):
        url = f"https://dev.azure.com/bachelor2024/{self.project_name}/_apis/wit/workitems/${type}?api-version=5"
        json = [
            {
                "op": "add", 
                "path": "/fields/System.Title", 
                "from": "null",
                "value": title
            },
            {
                "op": "add",
                "path": "/fields/System.Description", 
                "from": "null",
                "value": description
            },
            {
                "op": "add",
                "path": "/fields/System.History", 
                "from": "null",
                "value": comment
            }
        ]
        self.index += 1
        HttpPostResource(
            f"workitem{self.index}",
            url=url,
            headers=self.headers,
            json=json,
            auth=self.auth,
            opts=pulumi.ResourceOptions(depends_on=[self.depends_on])
        )

    def create_random_work_items(self, amount):
        #faker = Faker()
        work_item_type = [
            "Epic", 
            "Feature", 
            "User Story", 
            "Bug"
        ]
        work_item_title = [
            "Investigate production outage",
            "Add new feature",
            "Update documentation",
            "Refactor code",
            "Fix bug",
            "Add tests",
            "Update dependencies",
            "Add new endpoint"
        ]
        for i in range(amount):
            self.create(
                random.choice(work_item_type), 
                random.choice(work_item_title), 
                "This is a detailed description of the work item",
                f"Comment for task {i}"
            )
