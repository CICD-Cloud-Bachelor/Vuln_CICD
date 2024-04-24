# VULN3: Insufficient Credential Hygiene Challenge

## Overview

Vulnerability 3 addresses the issue highlighted by OWASP's CICD-SEC-6 from their top 10 list, focusing on Insufficient Credential Hygiene. This challenge underscores the common oversight where developers leave credentials in plaintext within the development environment, which can accidentally be forgotten and pushed to version control systems.

## Challenge Description

Participants will interact with a DevOps project containing a simple Python calculator application and its unit tests. The challenge revolves around a pipeline set to run these unit tests. However, the primary task is to find a forgotten token within the commit history of the repository.

## Environment Setup

The setup includes:
- An Azure DevOps project named "Vulnerability 3"
- A repository titled `python-calculator`
- A CI/CD pipeline named `Run unit tests`

The attacker, or participant, in this scenario has only read privileges on the resources, mimicking a situation where access is restricted yet sensitive information is still accessible due to past oversights.

## Technical Details

The repository inadvertently includes sensitive data — specifically, a token left in the commit history. The challenge is to uncover this token using available tools and access:

1. Review the commit history in the Azure repository directly through the web interface.
2. For a more efficient search, add an SSH public key to the repository, clone it locally, and then search the commit history using commands that look for keywords like "token", "pw", and "password".

## Running the Challenge

To begin the challenge, follow these steps:

1. Access the Azure DevOps environment using the provided credentials.
2. Navigate to the `python-calculator` repository.
3. Either browse the commit history online or clone the repository to your local machine after adding your SSH key for a more thorough search.
4. Identify and retrieve the forgotten token.

## Learning Objectives

- Understand the risks associated with poor credential management in development environments.
- Learn techniques for searching through repository histories for sensitive data.
- Highlight the importance of automated checks to prevent sensitive data from being committed.

This challenge serves as a practical exercise in identifying and mitigating risks in credential management within CI/CD processes, emphasizing the need for rigorous security practices even in seemingly low-risk areas.
