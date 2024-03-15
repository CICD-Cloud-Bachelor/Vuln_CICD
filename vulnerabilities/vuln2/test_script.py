import random

def generate_azure_it_ticket():
    # Templates for common Azure support requests
    templates = [
        "Cannot access Azure Virtual Machine named {resource_name}.",
        "Experiencing latency issues with Azure {service_name}.",
        "{resource_name} failed to deploy.",
        "Need additional permissions in Azure Active Directory for {user_role}.",
        "How do I configure {service_name} for high availability?",
        "Requesting increase in quota for {service_name}.",
        "Azure {service_name} is showing unexpected charges.",
        "Connectivity issues between Azure VPN Gateway and {resource_name}.",
        "Data recovery needed for Azure Blob Storage account named {resource_name}.",
        "Trouble setting up Azure AD Connect for {resource_name}."
    ]
    
    # Words to fill into the templates
    service_names = ["Virtual Networks", "SQL Database", "Function App", "Kubernetes Service", "Blob Storage"]
    resource_names = ["ResourceGroup1", "MyAzureVM", "StorageAccount", "SQLServerDB", "WebAppService"]
    user_roles = ["developer", "project manager", "data scientist", "system administrator", "network engineer"]
    
    # Select a random template
    template = random.choice(templates)
    
    # Fill the template with random choices
    ticket_description = template.format(
        service_name=random.choice(service_names),
        resource_name=random.choice(resource_names),
        user_role=random.choice(user_roles)
    )
    
    # Generate a title based on the template chosen
    # For simplicity, the title could be a shortened version or a specific part of the description
    if "{" in template:  # Check if template has placeholders to be filled
        title_start = template.split("{")[0]  # Get the text before the first placeholder
        ticket_title = title_start.strip() + " issue"  # Create a simple title
    else:
        ticket_title = template  # Use the template directly if no placeholders
    
    return ticket_title, ticket_description

# Generate and print a random Azure IT support ticket with title
ticket_title, ticket_description = generate_azure_it_ticket()
print(f"Title: {ticket_title}\nDescription: {ticket_description}")
