from _1_env_auth import HF_TOKEN

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

endpoint = HuggingFaceEndpoint(
    repo_id = "meta-llama/Llama-3.1-8B-Instruct",
    temperature = 0.5,
    huggingfacehub_api_token = HF_TOKEN,
)

llm = ChatHuggingFace(llm = endpoint)

