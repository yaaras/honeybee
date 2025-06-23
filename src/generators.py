import json
import re


def generate_from_prompt(client, model, prompt_file, user_prompt):
    """
    Generic function to generate content from the LLM.
    Expects the response to include a JSON block wrapped in markdown.
    """
    # Max try 5 times:
    for i in range(5):
        with open(prompt_file, "r") as f:
            system_prompt = f.read()
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=model,
        )
        api_response = chat_completion.choices[0].message.content
        try:
            json_text = re.search(r"```json(.*?)```$", api_response, re.DOTALL).group(1)
            return json.loads(json_text)
        except AttributeError:
            # Sometimes the AI doesnt return a valid json in markdown... simply try again.
            continue


def generate_dockerfile(client, model, application, misconfigurations):
    user_prompt = (
        f"Generate a Dockerfile for {application} with the following misconfigurations: "
        f"{', '.join(misconfigurations)}. Provide the output as a JSON object with 'file_name', 'file_path', and 'file_content' keys for each file."
    )
    return generate_from_prompt(
        client, model, "prompts/generate_dockerfile.md", user_prompt
    )


def generate_docker_compose(client, model, application, misconfigurations):
    user_prompt = (
        f"Generate a Docker Compose for {application} with the following misconfigurations: "
        f"{', '.join(misconfigurations)}. Provide the output as a JSON object with 'file_name', 'file_path', and 'file_content' keys for each file."
    )
    return generate_from_prompt(
        client, model, "prompts/generate_dockercompose.md", user_prompt
    )


def generate_nuclei(client, model, application, misconfigurations):
    user_prompt = (
        f"Generate a Nuclei template for {application} with the following misconfigurations: "
        f"{', '.join(misconfigurations)}. Return the template as JSON."
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": open("prompts/write_nuclei_rule.md").read()},
            {"role": "user", "content": user_prompt},
        ],
        model=model,
    )
    return chat_completion.choices[0].message.content


def generate_oval(client, model, application, misconfigurations):
    user_prompt = (
        f"Generate an Oval template for {application} with the following misconfigurations: "
        f"{', '.join(misconfigurations)}."
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": open("prompts/write_oval_rule.md").read()},
            {"role": "user", "content": user_prompt},
        ],
        model=model,
    )
    return chat_completion.choices[0].message.content
