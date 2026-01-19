from huggingface_hub import InferenceClient

HF_API_KEY = "HF Token"  # put your token here
MODEL_ID = "Model"

client = InferenceClient(model=MODEL_ID, token=HF_API_KEY)


def legal_agent(contract_text: str) -> str:
    prompt = f"""
    You are a Legal Expert.
    Task: Identify legal risks in the contract.
    Output format (JSON lines):
    {{
      "clause": "...",
      "risk": "...",
      "severity": "Low/Medium/High"
    }}

    CONTRACT:
    {contract_text}
    """

    messages = [{"role": "user", "content": prompt}]
    response = client.chat_completion(messages, max_tokens=800, temperature=0.3)

    return response.choices[0].message["content"].strip()

