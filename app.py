import zipfile
import streamlit as st
from openai import OpenAI, AzureOpenAI
import json
import re
import os


# Initialize OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-07-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Set page configuration
st.set_page_config(
    page_title="HoneyBee",
    page_icon=":bee:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🐝 HoneyBee")
st.subheader("Misconfiguration Simulator & Detector")
# Simulate, Misconfigure, Detect

application, dockerfile, nuclei = None, None, None

# Initialize session state variables if they don't exist
if "dockerfile_generated" not in st.session_state:
    st.session_state["dockerfile_generated"] = False
if "nuclei_generated" not in st.session_state:
    st.session_state["nuclei_generated"] = False
if "oval_generated" not in st.session_state:
    st.session_state["oval_generated"] = False

def create_files_from_json(root_dir, json_data):
    # Initialize list to collect all file paths for zipping later
    files = []

    # Process JSON data and create directories/files as specified
    for item in json_data:
        # Sanitize file paths and names
        file_name = re.sub(r'[^\w\-.]', '_', item["file_name"])  # Replace invalid characters in file names
        file_path = re.sub(r'[^\w\-./]', '_', item["file_path"])  # Replace invalid characters in paths

        # Construct the full path (relative to the root_dir)
        full_path = os.path.join(root_dir, file_path, file_name)

        # Ensure the directory structure exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Write file content
        with open(full_path, "w") as file:
            file.write(item["file_content"])
            files.append(full_path)  # Collect file path for later zipping

        print(f"Created {full_path}")

    return files


m1, m2, m3, m4 = st.columns([1,1,2,1])
custom_mode = m4.checkbox("Custom")
tab1, tab2, tab3 = st.tabs(["Dockerfile", "Nuclei", "Oval"])


with open('misconfigurations_new.json') as f:
    misconfigurations_data = json.loads(f.read())


if not custom_mode:
    # Standard mode with selectbox and multiselect
    categories = list(misconfigurations_data.keys())
    category = m1.selectbox("Choose a category:", categories)

    if category:
        applications = list(misconfigurations_data[category].keys())
        application = m2.selectbox("Choose an application:", applications)

        if application:
            misconfigurations = misconfigurations_data[category][application]
            selected_misconfigurations = m3.multiselect("Choose misconfigurations:", misconfigurations)

# custom mode with text inputs
else:
    application = m1.text_input("Enter application name:")
    misconfiguration = m2.text_input("Enter Misconfiguration:")

    selected_misconfigurations = [misconfiguration.strip()] if misconfiguration.strip() else []


with tab1:
    if application and st.button("Generate Dockerfile"):
        system_prompt = open('prompts/generate_dockerfile.md').read()
        user_prompt = (
            f"Generate a Dockerfile for {application} with the following misconfigurations: "
            f"{', '.join(selected_misconfigurations)}."
            f" Provide the output as a JSON object with 'file_name', 'file_path', and 'file_content' keys for each file."
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            model="gpt-4o-barak",
        )
        api_response = chat_completion.choices[0].message.content
        json_text = re.search(r'```json(.*?)```$', api_response, re.DOTALL).group(1)
        dockerfile = json.loads(json_text)
        st.session_state["dockerfile_generated"] = True
        st.session_state["dockerfile_content"] = dockerfile

    if st.session_state["dockerfile_generated"]:
        # st.json(st.session_state["dockerfile_content"])
        files_json = st.session_state["dockerfile_content"]
        col1, col2 = st.columns(2)
        for item in files_json:
            if item["file_type"] != "markdown":
                col1.caption(f"{item['file_path']}/{item['file_name']}")
                col1.code(item["file_content"], language="docker")
            else:
                col2.caption(f"{item['file_name']}")
                col2.markdown(item["file_content"])


        # Use the first misconfiguration to help name the folder
        misconfig = selected_misconfigurations[0].replace(' ', '_').lower()
        folder_name = f"{application}_{misconfig}"

        # Generate files based on GPT's Dockerfile JSON output
        files = create_files_from_json(application, st.session_state["dockerfile_content"])

        # Zip and download the generated files
        zip_filename = f"{folder_name}.zip"
        with open(zip_filename, "wb") as file:
            with zipfile.ZipFile(file, "w") as zip_file:
                for file_path in files:
                    zip_file.write(file_path)

        # Provide download button for the zip file
        data = open(zip_filename, "rb").read()
        st.download_button(f"Download {zip_filename}", data=data, file_name=zip_filename, on_click=None)

# with tab2:
#     if category and application and st.button("Generate Docker Compose"):
#         system_prompt = open('prompts/generate_dockercompose.md').read()
#         user_prompt = (
#             f"Generate a Docker Compose for {application} with the following misconfigurations: "
#             f"{', '.join(selected_misconfigurations)}."
#             f" Provide the output as a JSON object with 'file_name', 'file_path', and 'file_content' keys for each file."
#         )
#
#         chat_completion = client.chat.completions.create(
#             messages=[
#                 {
#                     "role": "system",
#                     "content": system_prompt,
#                 },
#                 {
#                     "role": "user",
#                     "content": user_prompt,
#                 }
#             ],
#             model="gpt-4o-barak",
#         )
#         api_response = chat_completion.choices[0].message.content
#         json_text = re.search(r'```json(.*?)```$', api_response, re.DOTALL).group(1)
#         dockercompose = json.loads(json_text)
#         st.session_state["dockercompose_generated"] = True
#         st.session_state["dockercompose_content"] = dockercompose
#
#     if st.session_state["dockercompose_generated"]:
#         files_json = st.session_state["dockercompose_content"]
#         col1, col2 = st.columns(2)
#         for item in files_json:
#             if item["file_type"] != "markdown":
#                 col1.caption(f"{item['file_path']}/{item['file_name']}")
#                 col1.code(item["file_content"], language="docker")
#             else:
#                 col2.caption(f"{item['file_name']}")
#                 col2.markdown(item["file_content"])
#
#
#         # Use the first misconfiguration to help name the folder
#         misconfig = selected_misconfigurations[0].replace(' ', '_').lower()
#         folder_name = f"{application}_{misconfig}"
#
#         # Generate files based on GPT's Dockerfile JSON output
#         files = create_files_from_json(application, st.session_state["dockercompose_content"])
#
#         # Zip and download the generated files
#         zip_filename = f"{folder_name}.zip"
#         with open(zip_filename, "wb") as file:
#             with zipfile.ZipFile(file, "w") as zip_file:
#                 for file_path in files:
#                     zip_file.write(file_path)
#
#         # Provide download button for the zip file
#         data = open(zip_filename, "rb").read()
#         st.download_button(f"Download {zip_filename}", data=data, file_name=zip_filename, on_click=None)

with tab2:
    if application and st.button("Generate Nuclei"):
        system_prompt = open('prompts/write_nuclei_rule.md').read()
        user_prompt = (f"Generate a Nuclei template for {application} with the following misconfigurations: "
                       f"{', '.join(selected_misconfigurations)}. Return the template as JSON.")
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model="gpt-4o-barak",
        )
        nuclei = chat_completion.choices[0].message.content
        st.session_state["nuclei_generated"] = True
        st.session_state["nuclei_content"] = nuclei

    if st.session_state["nuclei_generated"]:
        st.write(st.session_state["nuclei_content"])

with tab3:
    if application and st.button("Generate Oval"):
        system_prompt = open('prompts/write_oval_rule.md').read()
        user_prompt = (
            f"Generate an Oval template for {application} with the following misconfigurations: "
            f"{', '.join(selected_misconfigurations)}.")
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model="gpt-4o-barak",
        )
        oval = chat_completion.choices[0].message.content
        st.session_state["oval_generated"] = True
        st.session_state["oval_content"] = oval

    if st.session_state["oval_generated"]:
        st.write(st.session_state["oval_content"])
