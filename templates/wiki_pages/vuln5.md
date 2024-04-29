# Wiki: Automated Software Deployment via FTP

## Table of Contents
- [Introduction](#introduction)
- [System Components](#system-components)
- [FTP Server Configuration](#ftp-server-configuration)
- [Client Machine Setup](#client-machine-setup)
- [Deployment Process](#deployment-process)
- [Automated Execution on Client](#automated-execution-on-client)
- [Security Features](#security-features)
- [Monitoring and Logs](#monitoring-and-logs)
- [Troubleshooting](#troubleshooting)
- [Contacts](#contacts)

## Introduction
Welcome to the Automated Software Deployment system documentation. This system is designed for seamless software updates via an FTP server with automatic retrieval and execution by client systems.

## System Components
### Source Code Repository
- **Platform:** Azure Repos
- **Repository Name:** `deploy-software`

### Build and Release Tools
- **CI/CD:** Azure Pipelines
- **Artifact Storage:** Azure Artifacts

### FTP Server
- **Host:** ftp.examplecorp.com
- **Protocol:** SFTP for secure transfer

### Client Machines
- **Operating System:** Linux
- **Scheduled Tasks:** Cron jobs for software retrieval and execution

## FTP Server Configuration
1. **Access Configuration:** Setup with SSH key-based authentication to ensure secure access.
2. **Directory Structure:** All deployment artifacts are stored under `/var/www/software`.

## Client Machine Setup
Each client machine is configured with:
- **Cron Job:** Scheduled to check the FTP server every hour for new deployments.
- **Script Execution:** Bash scripts to execute new software upon download.

## Deployment Process
1. **Code Commit:** Developers push the latest code to the `deploy-software` repository.
2. **Build Pipeline:** Azure Pipelines compiles the code and runs tests.
3. **Release Pipeline:** Successful builds are packaged and uploaded to the FTP server.

## Automated Execution on Client
- **Retrieval Script:** Shell script to download and verify software integrity using checksums.
- **Execution:** Newly downloaded software is executed automatically, with parameters defined by the latest configuration files.

## Security Features
- **Encryption:** All data transferred via SFTP is encrypted.
- **Checksum Verification:** Ensures that the software has not been tampered with during transfer.

## Monitoring and Logs
- **Server Side:** FTP server logs all download activities.
- **Client Side:** Execution logs are retained for 30 days to facilitate debugging and verification.

## Troubleshooting
- **Common Issues:** Includes solutions to frequent issues like failed downloads, execution errors, and security warnings.
- **Support Contacts:** Listed in the contacts section for direct help from the system administrators.

## Contacts
- **System Administrator:** admin@examplecorp.com
- **Support Team:** support@examplecorp.com

