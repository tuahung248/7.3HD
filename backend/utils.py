import datetime

def log_interaction(question, role, result):
    log_entry = (
        f"{datetime.now().isoformat()} | Role: {role} | Question: {question} | "
        f"Response: {result['answer']}"
    )
    with open("interactions.log", "a") as logfile:
        logfile.write(log_entry + "\n")
