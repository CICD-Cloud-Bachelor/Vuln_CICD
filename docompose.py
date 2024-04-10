import subprocess

def run_docker_compose(command):
    """
    Runs a docker-compose command and prints its output.
    :param command: List of the command parts, e.g., ['up', '-d'] for 'docker-compose up -d'.
    """
    # Ensure the command is prefixed with 'docker-compose'
    docker_compose_cmd = ['docker-compose'] + command

    # Run the command
    process = subprocess.Popen(docker_compose_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for the command to complete
    stdout, stderr = process.communicate()
    
    if process.returncode == 0:
        print("Command executed successfully")
        print(stdout.decode())
    else:
        print("Error executing command")
        print(stderr.decode())

# Example usage:
if __name__ == "__main__":
    # Start containers in detached mode
    ctfd_path = "../Docker_Images/CTFd"
    run_docker_compose(['--project-directory', ctfd_path, 'up', '-d'])
    
    # Stop and remove containers, networks
    # run_docker_compose(['down'])
