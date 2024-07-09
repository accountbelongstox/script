import json
import os
from urllib.parse import urlparse


def extract_domains_from_har(har_file_path):
    # Load the HAR file
    with open(har_file_path, 'r', encoding='utf-8') as file:
        har_data = json.load(file)

    # Extract all request URLs
    urls = [entry['request']['url'] for entry in har_data['log']['entries']]

    # Extract and collect domain names from URLs
    domains = set()
    for url in urls:
        domain_name = urlparse(url).netloc
        domains.add(domain_name)

    # Print all unique domain names
    for domain in domains:
        print(domain)


# Main directory path
main_directory = os.path.join(os.environ['USERPROFILE'], 'Downloads')

# HAR file name
har_file_name = 'chatgpt.com.har'  # Replace with your HAR file name

# Full path to the HAR file
har_file_path = os.path.join(main_directory, har_file_name)

extract_domains_from_har(har_file_path)