# VULN1: Poisoned Pipeline Execution Challenge

## Overview

Vulnerability 1 exemplifies the Poisoned Pipeline Execution vulnerability from the OWASP Top 10 list. It focuses on an attack scenario where a secret variable within a CI/CD pipeline must be retrieved by modifying the pipeline's configuration file.

## Challenge Description

This challenge involves a repository and a CI/CD pipeline set to build code from the repository. The pipeline includes a secret flag utilized during the build process. The task for participants is to manipulate the pipeline configuration to expose and retrieve this secret flag.

## Environment Setup

The setup includes:
- An Azure DevOps project named "VULN1"
- A GitHub repository "VULN1_REPO"
- A pipeline "BUILD_PIPELINE"

Participants are provided with the ability to edit the repository and pipeline configurations, reflecting common scenarios where developers have access to modify CI/CD configurations.

## Technical Details

The pipeline is configured to compile and run a C program, with steps defined in the pipeline configuration file. By default, this file contains commands for installing dependencies, compiling the program, and running tests. The secret flag is used during these operations but is not exposed unless the pipeline is altered.

Participants will:
1. Edit the pipeline configuration file to include a command that sends the secret flag to an external server controlled by the participant.
2. Modify the build process to incorporate this new command.
3. Execute the pipeline and intercept the secret flag from the HTTP response.

## Running the Challenge

To start the challenge, follow these steps:

1. Access the Azure DevOps environment using provided credentials.
2. Navigate to the "VULN1_REPO" repository.
3. Modify the `BUILD_PIPELINE` configuration file to leak the secret flag, such as by adding a `curl` command that sends the flag to a server you control.
4. Commit the changes and run the pipeline.
5. Observe the output or intercept the network traffic to capture the secret flag.

## Learning Objectives

- Learn how to identify and exploit vulnerabilities in CI/CD pipelines.
- Understand the implications of allowing unrestricted edit access to pipeline configurations.
- Gain practical experience in securing pipelines against unauthorized modifications.

This challenge provides a comprehensive understanding of how seemingly benign pipeline configurations can be exploited to leak sensitive information, highlighting the importance of securing CI/CD environments against unauthorized changes.
