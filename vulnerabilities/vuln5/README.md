# VULN5: CI/CD Pipeline Security Challenge

## Overview

Vulnerability 5 is designed to simulate a real-world scenario where code is pushed to a central FTP server, and customers automatically retrieve updates from this server. This setup mirrors the one exploited in high-profile incidents like the SolarWinds attack. The challenge provides a hands-on experience for cybersecurity professionals to explore the risks and consequences of such vulnerabilities.

## Challenge Description

In this challenge, participants are tasked with exploiting a CI/CD pipeline to push malicious code to an FTP server that acts as a distributor to customers. The customers then download and run this application, potentially executing malicious activities like a reverse shell that can give attackers complete control over the customer's server.

## Environment Setup

The challenge uses an Azure DevOps CI/CD pipeline configured to build and deploy a fictional application to an FTP server, from which it is distributed to and run by customers. The environment setup includes:

- Azure DevOps project
- Code repository
- Automated build and deployment pipeline
- Permissions configurations


## Technical Details

The repository contains a C# application that, once built, is pushed to an FTP server. This setup demonstrates the vulnerability indexed as CICD-SEC-1: Insufficient Flow Control Mechanisms from OWASP, where insufficient validation and security controls in CI/CD pipelines can allow attackers to deploy malicious code.

## Running the Challenge

To initiate the challenge, follow these steps:

1. Start the environment using the provided script, which configures and runs the necessary Docker containers.
2. The setup script will deploy two main components:
   - `ftpserver`: Acts as the FTP server where the application is hosted.
   - `ftppoller`: Simulates the customer environment that polls the FTP server and downloads the application.
3. A web portal is also launched to facilitate interaction with the challenge, offering descriptions, difficulty ratings, and a submission interface for flags.

Participants are expected to retrieve the flag from the customer's server by exploiting the pipeline and pushing malicious code that includes a reverse shell.

## Learning Objectives

- Understand and identify weaknesses in CI/CD pipelines.
- Develop strategies to secure CI/CD environments against similar vulnerabilities.
- Gain practical experience in ethical hacking and penetration testing in cloud environments.

This challenge is an excellent opportunity for cybersecurity professionals to test their skills in a controlled, realistic setting and learn to better protect CI/CD pipelines from potential threats.
