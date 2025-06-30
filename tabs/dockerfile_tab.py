import streamlit as st
from src import generators, query_history

def render(application, input_mode, input_content, selected_misconfigs, client, model):
    if application and st.button("Generate Dockerfile", use_container_width=True, type="primary"):
        with st.spinner("Generating Dockerfile..."):
            if input_mode in ("import_url", "paste_input"):
                dockerfile = generators.generate_dockerfile_from_markdown(client, model, input_content)
            else:
                dockerfile = generators.generate_dockerfile(client, model, application, selected_misconfigs)
        st.session_state["dockerfile_generated"] = True
        st.session_state["dockerfile_content"] = dockerfile
        query_history.save_query("Dockerfile", [application, selected_misconfigs], dockerfile)
        st.success("Dockerfile generated successfully!")

    if st.session_state.get("dockerfile_generated"):
        files_json = st.session_state["dockerfile_content"]
        col1, col2 = st.columns(2)
        for item in files_json:
            if item.get("file_type") != "markdown":
                col1.caption(f"{item['file_path']}/{item['file_name']}")
                col1.code(item["file_content"], language="docker")
            else:
                col2.caption(item["file_name"])
                col2.markdown(item["file_content"])
