import yaml
import sys

def parse_docker_compose(file_path):
    with open(file_path, 'r') as file:
        compose_data = yaml.safe_load(file)
    return compose_data.get('services', {}).keys()

def copy_compose(file_path, selected_services, new_yml_path):
    # Load the original Docker Compose file
    with open(file_path, 'r') as file:
        compose_dict = yaml.safe_load(file)

    # Filter out only the selected services
    services = compose_dict.get('services', {})
    filtered_services = {name: details for name, details in services.items() if name in selected_services}

    # Update the services section of the compose dictionary
    compose_dict['services'] = filtered_services

    # Write the updated compose data to the new file
    with open(new_yml_path, 'w') as new_file:
        yaml.safe_dump(compose_dict, new_file)

def main():
    if len(sys.argv) < 2:
        print("Usage: yml_parse.py <function> [args]")
        sys.exit(1)

    function = sys.argv[1]

    if function == 'parse' and len(sys.argv) == 3:
        docker_compose_file = sys.argv[2]
        services = parse_docker_compose(docker_compose_file)
        for service in services:
            print(service)
    elif function == 'copy' and len(sys.argv) == 5:
        docker_compose_file = sys.argv[2]
        selected_services = sys.argv[3].split()
        new_yml_path = sys.argv[4]
        copy_compose(docker_compose_file, selected_services, new_yml_path)
    else:
        print("Python Script: yml_parse.py Invalid usage.")
        sys.exit(1)

if __name__ == "__main__":
    main()
