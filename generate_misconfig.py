from openai import OpenAI, AzureOpenAI
import json
import os
import yaml
import tqdm
import requests
from collections import defaultdict

client = AzureOpenAI(
    api_key="db975519918b40598305a9ca3e34fbed",
    api_version="2024-07-01-preview",
    azure_endpoint="https://ai-test-explorer-03.openai.azure.com/"
)


token = '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'
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
}

landscape_url = "https://raw.githubusercontent.com/cncf/landscape/master/landscape.yml"

def get_cncf_projects(url):
    # response = requests.get(url, headers=headers, verify=False)
    # if response.status_code == 200:
    with open('landscape.yml') as f:
        data = yaml.safe_load(f)
        projects = []
        for category in data['landscape']:
            if 'subcategories' in category:
                for subcategory in category['subcategories']:
                    if 'items' in subcategory:
                        for item in subcategory['items']:
                            project_info = {
                                'name': item['name'],
                                'homepage_url': item.get('homepage_url', 'N/A'),
                                'repo_url': item.get('repo_url', 'N/A'),
                                'description': item.get('description', 'N/A'),
                                'logo': item.get('logo', 'N/A'),
                                'category': category['name'],
                                'subcategory': subcategory['name']
                            }
                            projects.append(project_info)
        return projects
    # else:
    #     print("Failed to fetch data")
    #     return []

misconf_dict = {}

# landscape_data = get_cncf_projects(landscape_url)

landscape_data = [
    {'name': 'Jenkins', 'category': 'Development Tools'},
    {'name': 'Apache ActiveMQ', 'category': 'Messaging Systems'},
    {'name': 'Apache Kafka', 'category': 'Messaging Systems'},
    {'name': 'Apache Airflow', 'category': 'Data Processing'},
    {'name': 'Apache NiFi', 'category': 'Data Processing'},
    {'name': 'Apache Flink', 'category': 'Data Processing'},
    {'name': 'Apache Hadoop', 'category': 'Data Processing'},
    {'name': 'Apache Spark', 'category': 'Data Processing'},
    {'name': 'Apache Storm', 'category': 'Data Processing'},
    {'name': 'Apache Tomcat', 'category': 'Web Servers'},
    {'name': 'Redis', 'category': 'Databases'},
    {'name': 'PostgreSQL', 'category': 'Databases'},
    {'name': 'NGINX', 'category': 'Web Servers'},
    {'name': 'Jupyter Lab', 'category': 'Development Tools'},
    {'name': 'Jupyter Notebook', 'category': 'Development Tools'},
    {'name': 'Laravel', 'category': 'Development Tools'}
]

# Initialize a dictionary to hold the structured data
structured_output = defaultdict(lambda: defaultdict(list))

for application in tqdm.tqdm(landscape_data, total=len(landscape_data)):
    system_prompt = open('prompts/list_misconfig.md').read()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": f"INPUT:{application['name']}\nOUTPUT:",
            }
        ],
        model="gpt-4o-barak",
    )
    output_json = chat_completion.choices[0].message.content
    output_json = output_json.strip('json').strip('`').strip('json').strip()

    print(output_json)

    try:
        misconfigs = json.loads(output_json)['misconfigurations']
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        misconfigs = []

    # Structure the data
    category = application['category']
    app_name = application['name']
    structured_output[category][app_name].extend(misconfigs)

# Convert defaultdict to a regular dictionary for saving
structured_output = {category: dict(apps) for category, apps in structured_output.items()}

# Save to JSON
with open('misconfigurations_new.json', 'w') as f:
    json.dump(structured_output, f, indent=4)



