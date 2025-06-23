import os
import streamlit as st


def get_llm_settings():
    st.sidebar.header("Settings ⚙️")

    # Use session state to set default provider; default to "OpenAI" if not set
    default_provider = st.session_state.get("provider", "OpenAI")
    provider_options = ["OpenAI", "Azure OpenAI"]
    default_index = (
        provider_options.index(default_provider)
        if default_provider in provider_options
        else 0
    )
    provider = st.sidebar.selectbox(
        "Select LLM Provider",
        provider_options,
        key="provider_select",
        index=default_index,
    )
    st.session_state["provider"] = provider
    settings = {"provider": provider}

    if provider == "OpenAI":
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            default_openai_key = st.session_state.get("openai_api_key", "")
            openai_api_key = st.sidebar.text_input(
                "Enter your OpenAI API Key",
                type="password",
                key="openai_api_key",
                value=default_openai_key,
            )
        else:
            st.sidebar.info("Using OpenAI API Key from environment variable")
        settings["api_key"] = openai_api_key

        default_model = st.session_state.get("model", "gpt-4")
        model = st.sidebar.text_input(
            "Model",
            value=default_model,
            help="Enter the OpenAI model to use",
            key="model_input",
        )
        settings["model"] = model
    else:
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not azure_api_key:
            default_azure_key = st.session_state.get("azure_api_key", "")
            azure_api_key = st.sidebar.text_input(
                "Enter your Azure OpenAI API Key",
                type="password",
                key="azure_api_key",
                value=default_azure_key,
            )
        else:
            st.sidebar.info("Using Azure OpenAI API Key from env")
        settings["api_key"] = azure_api_key

        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not azure_endpoint:
            default_endpoint = st.session_state.get("azure_endpoint", "")
            azure_endpoint = st.sidebar.text_input(
                "Enter your Azure OpenAI Endpoint",
                key="azure_endpoint",
                value=default_endpoint,
            )
        settings["azure_endpoint"] = azure_endpoint

        default_model = st.session_state.get("model", "gpt-4o-barak")
        model = st.sidebar.text_input(
            "Model",
            value=default_model,
            help="Enter the Azure OpenAI model to use",
            key="model_input",
        )
        settings["model"] = model

    # Save the model in session state for later use
    st.session_state["model"] = settings["model"]

    return settings
