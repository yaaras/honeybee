from openai import OpenAI, AzureOpenAI
import json
import os
import yaml
import tqdm
import requests
from collections import defaultdict

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-07-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)


token = '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'
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
}

landscape_url = "https://raw.githubusercontent.com/cncf/landscape/master/landscape.yml"

# read the misconfigurations json
with open('misconfigurations_new.json', 'r') as f:
    misconfig_dict = json.load(f)



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



