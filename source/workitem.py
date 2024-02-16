from pulumi.dynamic import ResourceProvider, Resource, CreateResult
import pulumi_azuredevops as azuredevops
import pulumi, random
import configparser
from source.azure_devops_rest_api import HttpPostResource

config = configparser.ConfigParser()
config.read('config.ini')
USERNAME = config["AZURE"]["USERNAME"]
PAT = config["AZURE"]["PAT"]


class WorkItem:
    index = 0
    def __init__(
            self, 
            organization_name: str, 
            project_name: str, 
            depends_on: list[Resource]
        ) -> None:
        self.organization_name = organization_name
        self.project_name = project_name
        self.auth = (USERNAME, PAT)
        self.headers = {"Content-Type": "application/json-patch+json"}
        self.depends_on = depends_on

    def create(
            self, 
            type: str, 
            title: str, 
            description: str, 
            comments: list[str],
            email: str = None
        ) -> None:
        #####
        #Dette blir feil. Her settes url-en til å være for kort hvis det er flere enn en kommentar. Da vil det postes til den for korte urlen og det funker ikke. FIKS
        #####
        url = f"https://dev.azure.com/{self.organization_name}/{self.project_name}/_apis/wit/workitems/"

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
            }
        ]
        if email is not None:
            json.append(
                {
                    "op": "add",
                    "path": "/fields/System.AssignedTo", 
                    "value": email
                }
            )
        
        self.index += 1
        HttpPostResource(
            name=f"workitem{self.index}",
            url=url,
            headers=self.headers,
            json=json,
            auth=self.auth,
            type=type,
            comments=comments,
            opts=pulumi.ResourceOptions(depends_on=self.depends_on),
        )

    def create_random_work_items(
            self, 
            amount: int,
            users: list[azuredevops.User] = None
        ) -> None:

        work_item_type = [
            "Epic", 
            "Feature", 
            "Task"
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
                type=random.choice(work_item_type), 
                title=random.choice(work_item_title), 
                description="This is a detailed description of the work item",
                comments=[f"Comment for task {i}"],
                email=random.choice(users).principal_name if users is not None else None
            )
