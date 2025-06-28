import streamlit as st
from src import generators, query_history

def render(application, input_mode, input_content, selected_misconfigs, client, model):
    if application and st.button("Generate Nuclei", use_container_width=True, type="primary"):
        with st.spinner("Generating Nuclei..."):
            if input_mode in ("import_url", "paste_input"):
                nuclei = generators.generate_nuclei_from_markdown(client, model, input_content)
            else:
                nuclei = generators.generate_nuclei(client, model, application, selected_misconfigs)
        st.session_state["nuclei_generated"] = True
        st.session_state["nuclei_content"] = nuclei
        query_history.save_query("Nuclei", [application, selected_misconfigs], nuclei)
        st.success("Nuclei generated successfully!")

    if st.session_state.get("nuclei_generated"):
        st.write(st.session_state["nuclei_content"])
