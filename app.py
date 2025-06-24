import requests
import streamlit as st
import json
import time
from src.settings import get_llm_settings, get_jina_ai_api_key
from src.client_provider import get_llm_client
from src.validations import run_yamlfix
from src.trace_tools import add_tcpdump_service
from src.local_deploy import local_deploy_compose
import src.generators as generators
import src.query_history as query_history

# Set up Streamlit page
st.set_page_config(
    page_title="HoneyBee",
    page_icon=":bee:",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("🐝 HoneyBee")
st.subheader("Misconfigured App Simulator & Detector")

# Get LLM settings from the sidebar
settings = get_llm_settings()

# Validate API credentials
if settings["provider"] == "OpenAI" and not settings["api_key"]:
    st.warning("Please provide your OpenAI API Key in the Settings.")
    st.stop()
elif settings["provider"] == "Azure OpenAI" and (
    not settings.get("api_key") or not settings.get("azure_endpoint")
):
    st.warning("Please provide your Azure OpenAI API Key and Endpoint in the Settings.")
    st.stop()

# Initialize LLM client and model
client = get_llm_client(settings)
model = settings["model"]

# Get Jina AI API key
jina_ai_api = get_jina_ai_api_key()

# Load misconfigurations data
with open("misconfigurations_catalog.json") as f:
    misconfigurations_data = json.load(f)


# Calculate metrics from the JSON data
apps_count = 0
misconfigs_count = 0

for category, apps_dict in misconfigurations_data.items():
    apps_count += len(apps_dict)
    for app, misconfigs in apps_dict.items():
        misconfigs_count += len(misconfigs)

# Show metrics in the sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Metrics")
s1, s2 = st.sidebar.columns(2)
s1.metric("Apps", apps_count)
s2.metric("Misconfigs", misconfigs_count)

# input options
browse_catalog = ":material/sort: Browse Catalog"
custom_input = ":material/manage_search: Custom Input"
import_url = ":material/add_link: Import from URL"
paste_input = ":material/content_paste: Paste Content"

input_mode = st.segmented_control(
    "How do you want to provide your input?",
    options=[browse_catalog, custom_input, import_url, paste_input],
    default=browse_catalog,
)

# prepare outputs
selected_misconfigurations = []
input_content = None

# load from list of misconfigurations
if input_mode == browse_catalog:
    m1, m2, m3 = st.columns([1, 1, 2])
    categories = list(misconfigurations_data.keys())
    category  = m1.selectbox("Choose a category:", categories)
    if category:
        applications = list(misconfigurations_data[category].keys())
        application = m2.selectbox("Choose an application:", applications)
        if application:
            misconfigs = misconfigurations_data[category][application]
            selected_misconfigurations = m3.multiselect(
                "Choose misconfigurations:", misconfigs
            )

# load from custom input
elif input_mode == custom_input:
    m1, m2 = st.columns([1, 3])
    application = m1.text_input("Enter application name:")
    misconfig    = m2.text_input("Enter Misconfiguration:")
    selected_misconfigurations = [misconfig.strip()] if misconfig.strip() else []

# load from URL
elif input_mode == import_url:
    url = st.text_input(
        "Enter URL to scrape and convert to Markdown:",
        value=st.session_state.get("url", ""),
        help="Hit Enter or click away to load."
    )
    st.session_state.url = url

    if not jina_ai_api:
        st.warning("Please provide your Jina AI API Key in the Settings.")
        st.stop()

    if url:
        with st.spinner("Loading URL content..."):
            # call Jina-AI proxy
            jina_ai_url = f"https://r.jina.ai/{url}"
            resp = requests.get(
                jina_ai_url,
                headers={"Authorization": f"Bearer {jina_ai_api}"}
            )
            if resp.status_code == 200:
                input_content = resp.text
                # max length is 8192 characters, so we truncate it
                input_content = input_content[:8192]
                st.success("✅ URL content loaded successfully!")
                with st.expander("URL Content Preview", expanded=False):
                    st.code(input_content, language="markdown")
            else:
                st.error(f"Failed to fetch URL (status {resp.status_code})")

else:
    # Manual input mode
    application = st.text_input(
        "Enter application name:",
        value=st.session_state.get("application", ""),
        help="Enter the name of the application you want to simulate."
    )
    st.session_state.application = application

    input_content = st.text_area(
        "Enter custom text:",
        value=st.session_state.get("input_content", ""),
        height=200,
        help="Enter custom text to generate configurations."
    )
    st.session_state.input_content = input_content
    if input_content:
        # max length is 8192 characters, so we truncate it
        input_content = input_content[:8192]

if input_mode == import_url and input_content:
    prompt_source = input_content
    application = generators.extract_application_from_markdown(client, model, input_content)
elif input_mode == paste_input and input_content:
    prompt_source = input_content
    application = st.session_state.get("application", "")
    if not application:
        st.warning("Please enter an application name.")
        st.stop()
else:
    prompt_source = "\n".join(selected_misconfigurations)

if not prompt_source.strip():
    st.warning("Please select misconfigurations, enter custom text, or provide a URL.")
    st.stop()


# TABS

# Create tabs for different generators
dockercompose_tab, dockerfile_tab, nuclei_tab, history_tab = st.tabs(
    ["Docker Compose", "Dockerfile", "Nuclei", "History"]
)

# Dockerfile Tab
with dockerfile_tab:
    if application and st.button("Generate Dockerfile", use_container_width=True, type="primary"):
        with st.spinner("Generating Dockerfile..."):
            if input_mode in (import_url, paste_input):
                dockerfile = generators.generate_dockerfile_from_markdown(
                    client, model, input_content
                )
            else:
                dockerfile = generators.generate_dockerfile(
                    client, model, application, selected_misconfigurations
                )
        st.session_state["dockerfile_generated"] = True
        st.session_state["dockerfile_content"] = dockerfile
        query_history.save_query(
            "Dockerfile", [application, selected_misconfigurations], dockerfile
        )
        st.success("Dockerfile generated successfully!")

    if st.session_state.get("dockerfile_generated"):
        files_json = st.session_state["dockerfile_content"]
        col1, col2 = st.columns(2)
        for item in files_json:
            if item.get("file_type") != "markdown":
                col1.caption(f"{item['file_path']}/{item['file_name']}")
                col1.code(item["file_content"], language="docker")
            else:
                col2.caption(f"{item['file_name']}")
                col2.markdown(item["file_content"])

# Docker Compose Tab
with dockercompose_tab:
    with_trace = st.toggle(
        "With trace tools",
        help="Choose to add trace services to the docker compose for example tcpdump",
    )
    if application and st.button(
        "Generate Docker Compose", use_container_width=True, type="primary"
    ):
        with st.spinner("Generating Docker Compose..."):
            if input_mode in (import_url, paste_input):
                dockercompose = generators.generate_docker_compose_from_markdown(
                    client, model, input_content
                )
            else:
                dockercompose = generators.generate_docker_compose(
                    client, model, application, selected_misconfigurations
                )
            for item in dockercompose:
                if item["file_type"].lower() == "yaml":
                    # Try to imporove the docker-compose output using yamlfix.
                    fixed_code = run_yamlfix(item["file_content"])
                    if with_trace:
                        # Add the tcpdump service
                        fixed_code = add_tcpdump_service(fixed_code)
                    item["file_content"] = fixed_code

        st.session_state["dockercompose_generated"] = True
        st.session_state["dockercompose_content"] = dockercompose
        query_history.save_query(
            "Docker Compose", [application, selected_misconfigurations], dockercompose
        )
        st.success("Docker Compose generated successfully!")

    if st.session_state.get("dockercompose_generated"):
        files_json = st.session_state["dockercompose_content"]
        col1, col2 = st.columns(2)
        for item in files_json:
            if item.get("file_type") != "markdown":
                col1.caption(f"{item['file_path']}/{item['file_name']}")
                col1.code(item["file_content"], language="yaml")
            else:
                col2.caption(f"{item['file_name']}")
                col2.markdown(item["file_content"])
    if st.session_state.get("dockercompose_generated") and st.button("Deploy Locally"):
        files_json = st.session_state["dockercompose_content"]
        for item in files_json:
            if item.get("file_type").lower() == "yaml":
                local_deploy_compose(item["file_content"])
    if final_output := st.session_state.get("deploy_process_output"):
        st.code(
            "\n".join(final_output),
            height=400,
            line_numbers=True,
            wrap_lines=True,
        )
        st.button("Stop Local Deploy", disabled=True)
        st.session_state["deploy_process_output"] = None

# Nuclei Tab
with nuclei_tab:
    if application and st.button("Generate Nuclei", use_container_width=True, type="primary"):
        with st.spinner("Generating Nuclei..."):
            if input_mode in (import_url, paste_input):
                nuclei = generators.generate_nuclei_from_markdown(
                    client, model, input_content
                )
            else:
                nuclei = generators.generate_nuclei(
                    client, model, application, selected_misconfigurations
                )
        st.session_state["nuclei_generated"] = True
        st.session_state["nuclei_content"] = nuclei
        query_history.save_query(
            "Nuclei", [application, selected_misconfigurations], nuclei
        )
        st.success("Nuclei generated successfully!")

    if st.session_state.get("nuclei_generated"):
        st.write(st.session_state["nuclei_content"])

