from collections import defaultdict

user_memory = defaultdict(list)

def get_user_history(user_id: str):
    return user_memory[user_id]

def add_to_history(user_id: str, role: str, content: str):
    user_memory[user_id].append({"role": role, "content": content})

def clear_user_history(user_id: str):
    user_memory[user_id] = []
