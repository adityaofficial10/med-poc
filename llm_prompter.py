def build_prompt(question: str, chunks: list[str]) -> str:
    context = "\n\n".join(chunks)
    return f"""You are a medical assistant. Based only on the following medical test report text, answer the question precisely.

--- Medical Report Data (retrieved) ---
{context}
----------------------------------------

Question: {question}
Answer:"""


def build_prompt_beta(question: str, grouped_chunks: dict) -> str:
    """
    Format prompt to clearly separate report dates and include relevant context
    """
    context_blocks = []
    
    # Sort filenames chronologically (assuming timestamp is in filename or metadata)
    sorted_files = sorted(grouped_chunks.keys())

    for fname in sorted_files:
        chunks = grouped_chunks[fname]
        context_blocks.append(f"--- Report: {fname} ---\n" + "\n".join(chunks))

    context = "\n\n".join(context_blocks)

    prompt = f"""
You are a medical assistant helping a patient understand their lab report history.

Below are their medical test results from different reports:

{context}

Now answer the following question based on the historical data provided:

Question: {question}
Answer:"""

    return prompt