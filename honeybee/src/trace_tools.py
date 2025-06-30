import oyaml as yaml
from src.validations import run_yamlfix


def add_tcpdump_service(docker_yaml):
    docker_yaml = yaml.safe_load(docker_yaml)
    main_service = [
        service_name
        for service_name, values in docker_yaml["services"].items()
        if values.get("ports", None)
    ][0]
    tcpdump_service = {
        "image": "corfr/tcpdump@sha256:3006b3bd9f041bf73f21e626b97cca5e78fd6ce271549ca95b8e6a508165512b",
        "restart": "always",
        "network_mode": f"service:{main_service}",
        "volumes": ["./:/data"],
    }
    docker_yaml["services"]["tcpdump"] = tcpdump_service
    return run_yamlfix(yaml.safe_dump(docker_yaml))
