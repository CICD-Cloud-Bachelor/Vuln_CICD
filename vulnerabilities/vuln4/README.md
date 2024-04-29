# VULN4: CI/CD Identity and Access Management Challenge

## Overview

Vulnerability 4 illustrates a critical aspect of CI/CD security, inspired by the CICD-SEC-2 item on the OWASP Top 10 CI/CD list. It showcases a vulnerability stemming from inadequate identity and access management in DevOps environments, where numerous accounts may have extensive privileges over the build systems.

## Challenge Description

In this challenge, participants engage with a repository and a pipeline deploying a MySQL database. The pipeline contains secret variables storing connection details, including passwords. The objective is to gain access to the database and retrieve the password for the user "Troll_Trollington", presented as `FLAG{password}`.

## Environment Setup

The challenge setup involves:
- An Azure DevOps project
- A repository named `VULN4_REPO`
- A CI/CD pipeline named `pipeline`
- A MySQL database deployed via Docker container

Participants are provided with a pipeline that has permissions only to build, with the rest of the Azure DevOps environment being read-only. The repository does not allow file editing but permits file viewing, including viewing the pipeline build file which uses credentials to connect to the database.

## Technical Details

The pipeline secretly stores credentials that are essential for database access. These credentials are exposed only during the pipeline's execution, where they are compiled into the build process results, specifically into an `AppSettings.json` file. Participants need to initiate the pipeline to compile and reveal the `AppSettings.json`, after which they can use the exposed credentials to access the database and attempt to crack the password hash.

## Running the Challenge

To start the challenge, follow these steps:

1. Use the provided script to configure and launch the necessary Docker container for the MySQL database.
2. Navigate to the Azure DevOps environment to interact with the pre-configured CI/CD pipeline.
3. Run the pipeline to build the application and reveal the `AppSettings.json` file with the database credentials.
4. Access the database using these credentials and locate the password for "Troll_Trollington".

## Learning Objectives

- Understand the vulnerabilities associated with improper identity and access management in CI/CD environments.
- Learn how to manage secrets and sensitive information within CI/CD pipelines.
- Gain insights into securing DevOps environments against unauthorized access and potential exploits.

This challenge is designed to provide practical experience with managing access controls and securing sensitive data within a CI/CD pipeline, highlighting the importance of strict identity and access management practices in modern software development environments.
