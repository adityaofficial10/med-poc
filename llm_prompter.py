# llm_prompter.py
def build_prompt(question: str, chunks: list[str]) -> str:
    context = "\n\n".join(chunks)
    return f"""You are a medical assistant. Based only on the following medical test report text, answer the question precisely.

--- Medical Report Data (retrieved) ---
{context}
----------------------------------------

Question: {question}
Answer:"""
