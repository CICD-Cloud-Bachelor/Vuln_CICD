from python_on_whales import DockerClient

if __name__ == "__main__":
    docker = DockerClient(compose_files=["../Docker_Images/CTFd/docker-compose.yml"])

    docker.compose.up()
   