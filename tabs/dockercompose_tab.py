import streamlit as st
from src.validations import run_yamlfix
from src.trace_tools import add_tcpdump_service
from src.local_deploy import local_deploy_compose
from src import generators, query_history

def render(application, input_mode, input_content, selected_misconfigs, client, model, docker_compose_supported):
    with_trace = st.toggle("With trace tools", help="Add tcpdump service")
    if application and st.button("Generate Docker Compose", use_container_width=True, type="primary"):
        with st.spinner("Generating Docker Compose..."):
            if input_mode in ("import_url", "paste_input"):
                comps = generators.generate_docker_compose_from_markdown(client, model, input_content)
            else:
                comps = generators.generate_docker_compose(client, model, application, selected_misconfigs)

            for item in comps:
                if item["file_type"].lower() == "yaml":
                    code = run_yamlfix(item["file_content"])
                    if with_trace:
                        code = add_tcpdump_service(code)
                    item["file_content"] = code

        st.session_state["dockercompose_generated"] = True
        st.session_state["dockercompose_content"] = comps
        query_history.save_query("Docker Compose", [application, selected_misconfigs], comps)
        st.success("Docker Compose generated successfully!")

    if st.session_state.get("dockercompose_generated"):
        files_json = st.session_state["dockercompose_content"]
        col1, col2 = st.columns(2)
        for item in files_json:
            if item.get("file_type") != "markdown":
                col1.caption(f"{item['file_path']}/{item['file_name']}")
                col1.code(item["file_content"], language="yaml")
            else:
                col2.caption(item["file_name"])
                col2.markdown(item["file_content"])

    if st.session_state.get("dockercompose_generated") and st.button(
        "Deploy Locally", use_container_width=True, type="primary", disabled=not docker_compose_supported
    ):
        for item in st.session_state["dockercompose_content"]:
            if item.get("file_type").lower() == "yaml":
                local_deploy_compose(item["file_content"])
