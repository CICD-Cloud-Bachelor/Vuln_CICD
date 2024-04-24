# VULN2: Insufficient Credential Hygiene and Access Management Challenge

## Overview

Vulnerability 2 explores multiple security issues, focusing on Insufficient Credential Hygiene (OWASP CICD-SEC6), Inadequate Identity and Access Management (OWASP CICD-SEC2), and Insecure System Configuration (OWASP CICD-SEC7). This challenge highlights the dangers of poor security practices that may lead to unauthorized access and potential supply chain attacks.

## Challenge Description

Participants are introduced to a scenario where an IT department manages development with default credentials that are widely known and not regularly updated. A user, mistakenly not removed from a project, gains access to a secret project nearing completion, which includes a Remote Code Execution (RCE) vulnerability within its source code.

## Environment Setup

The setup involves:
- Two Azure DevOps projects: one for the IT Department and another for a highly confidential project.
- Both projects include a variety of work items and a wiki page that inadvertently reveal sensitive information.
- The secret project is in its final development stages, with an impending deployment that participants need to secure or exploit.

## Technical Details

The IT department's project contains various work items and a wiki page detailing default login credentials and procedures. The secret project's development involves critical components like an admin panel with known vulnerabilities. 

Participants will exploit the scenario by:
1. Accessing the IT department's wiki to retrieve default credentials.
2. Using these credentials to access the secret project's repository.
3. Identifying and exploiting the RCE vulnerability within the source code of the admin panel.

## Running the Challenge

To initiate the challenge, follow these steps:

1. Review the IT department’s wiki for default credentials.
2. Access the secret project using these credentials.
3. Navigate to the repository and inspect the commit history for the admin panel's source code.
4. Exploit the RCE vulnerability detailed in the work items to execute arbitrary code on the admin panel.

## Learning Objectives

- Understand the risks and consequences of poor credential management and inadequate access controls.
- Learn to identify and exploit vulnerabilities within CI/CD environments that could lead to severe security breaches.
- Gain practical experience in ethical hacking techniques specific to software development and deployment processes.

This challenge provides a comprehensive exercise in securing or exploiting complex systems, emphasizing the need for stringent security practices and regular audits within software development projects.
