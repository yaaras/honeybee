import streamlit as st
import json
import time
from src.settings import get_llm_settings
from src.client_provider import get_llm_client
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
col1, col2 = st.sidebar.columns(2)
col1.metric("Apps", apps_count)
col2.metric("Misconfigs", misconfigs_count)

# Toggle for custom mode
custom_mode = st.toggle("Custom")
placeholder = st.empty()

# Define UI columns based on mode
if not custom_mode:
    with placeholder.container():
        m1, m2, m3 = st.columns([1, 1, 2])
        categories = list(misconfigurations_data.keys())
        category = m1.selectbox("Choose a category:", categories)
        if category:
            applications = list(misconfigurations_data[category].keys())
            application = m2.selectbox("Choose an application:", applications)
            if application:
                misconfigs = misconfigurations_data[category][application]
                selected_misconfigurations = m3.multiselect(
                    "Choose misconfigurations:", misconfigs
                )
else:
    with placeholder.container():
        m1, m2, m3 = st.columns([1, 3, 1])
        application = m1.text_input("Enter application name:")
        misconfig = m2.text_input("Enter Misconfiguration:")
        selected_misconfigurations = [misconfig.strip()] if misconfig.strip() else []

# Create tabs for different generators
dockerfile_tab, dockercompose_tab, nuclei_tab, history_tab = st.tabs(
    ["Dockerfile", "Docker Compose", "Nuclei", "History"]
)

# Dockerfile Tab
with dockerfile_tab:
    if application and st.button("Generate Dockerfile"):
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
    if application and st.button("Generate Docker Compose"):
        dockercompose = generators.generate_docker_compose(
            client, model, application, selected_misconfigurations
        )
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

# Nuclei Tab
with nuclei_tab:
    if application and st.button("Generate Nuclei"):
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


@st.dialog(title="Run History", width="large")
def display_history_result(type, output):
    st.write(
        """<style>
        .stDialog *[role="dialog"] {
            width: 85%;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    if type in ("Dockerfile", "Docker Compose"):
        files_json = output
        col1, col2 = st.columns(2)
        for item in files_json:
            if item.get("file_type") != "markdown":
                col1.caption(f"{item['file_path']}/{item['file_name']}")
                col1.code(item["file_content"], language="docker")
            else:
                col2.caption(f"{item['file_name']}")
                col2.markdown(item["file_content"])
    elif type == "Nuclei":
        st.write(output)


# History tab
with history_tab:
    history_data = query_history.load_history()
    # Show the latest queries first
    historical_queries = sorted(history_data.items(), reverse=True)
    with st.container(height=800):
        for q_time, q_data in historical_queries:
            with st.container(border=True):
                (runtime_col,) = st.columns(1)
                tech_col, misconfigs_col = st.columns(2)
                (load_col,) = st.columns(1)
                runtime_col.text(time.ctime(float(q_time)))
                tech, misconfigs = q_data["input_parameters"]
                tech_col.selectbox(
                    "Application",
                    options=[tech],
                    index=0,
                    disabled=True,
                    key=f"{q_time}_{tech}",
                )
                misconfigs_col.multiselect(
                    "Misconfigurations",
                    options=misconfigs,
                    default=misconfigs,
                    disabled=True,
                    key=f"{q_time}_{misconfigs}",
                )
                load_col.button(
                    f"Load {q_data['type']}",
                    key=f"{q_time}_{q_data['type']}",
                    on_click=display_history_result,
                    args=(q_data["type"], q_data["output"]),
                )
