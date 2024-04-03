Setup:
You get creds for a user to login as. This user does not have permissions to build the pipeline. There exists creds for another user in the wiki/work item comments which have access to build the pipeline, but not to edit the repo.

The goal is to find the password, username and connection string to the database used by the application. This can be found in the artifacts produced by the build. Login to that db and find the password for the user "Troll Trollington". That is the flag.