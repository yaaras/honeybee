import os
import streamlit as st


def get_llm_settings():
    st.sidebar.header("Settings ⚙️")
    provider = st.sidebar.selectbox("Select LLM Provider", ["OpenAI", "Azure OpenAI"])
    settings = {"provider": provider}

    if provider == "OpenAI":
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            openai_api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
        else:
            st.sidebar.info("Using OpenAI API Key from env")
        settings["api_key"] = openai_api_key
        settings["model"] = st.sidebar.text_input("Model", value="gpt-4", help="Enter the OpenAI model to use")
    else:
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not azure_api_key:
            azure_api_key = st.sidebar.text_input("Enter your Azure OpenAI API Key", type="password")
        else:
            st.sidebar.info("Using Azure OpenAI API Key from env")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not azure_endpoint:
            azure_endpoint = st.sidebar.text_input("Enter your Azure OpenAI Endpoint")
        settings["api_key"] = azure_api_key
        settings["azure_endpoint"] = azure_endpoint
        settings["model"] = st.sidebar.text_input("Model", value="gpt-4o-barak",
                                                  help="Enter the Azure OpenAI model to use")

    return settings
