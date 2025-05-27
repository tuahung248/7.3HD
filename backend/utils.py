from datetime import datetime

def log_interaction(question, role, result):
    # For real app: send to database or logging system
    log_entry = f"{datetime.now().isoformat()} | Role: {role} | Question: {question} | Response: {result['answer']}"
    with open("interactions.log", "a") as logf:
        logf.write(log_entry + "\n")
