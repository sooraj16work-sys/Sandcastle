import ollama
import json
import os

MEMORY_FILE = 'memory.json'

system_message = {
    'role': 'system',
    'content': 'You are a helpful, direct, and friendly AI assistant.'
}

# Load old conversation if it exists
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, 'r') as f:
        conversation = json.load(f)
    print("Memory loaded — I remember our previous chats!\n")
else:
    conversation = [system_message]

print("=== AI SESSION STARTED ===")
print("Type 'exit' to quit, 'clear' to reset memory.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == 'exit':
        with open(MEMORY_FILE, 'w') as f:
            json.dump(conversation, f)
        print("Memory saved. See you next time!")
        break

    if user_input.lower() == 'clear':
        conversation = [system_message]
        os.remove(MEMORY_FILE)
        print("Memory cleared.\n")
        continue

    conversation.append({'role': 'user', 'content': user_input})
    response = ollama.chat(model='qwen2.5-coder:7b', messages=conversation)
    reply = response['message']['content']
    conversation.append({'role': 'assistant', 'content': reply})
    print(f"\nAI: {reply}\n")
