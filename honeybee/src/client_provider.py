from openai import OpenAI, AzureOpenAI

def get_llm_client(settings):
    provider = settings["provider"]
    if provider == "OpenAI":
        return OpenAI(api_key=settings["api_key"])
    elif provider == "Azure OpenAI":
        return AzureOpenAI(
            api_key=settings["api_key"],
            api_version="2024-07-01-preview",
            azure_endpoint=settings["azure_endpoint"]
        )
