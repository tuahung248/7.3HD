import datetime


def log_interaction(question, role, result):
    log_entry = (
        f"{datetime.datetime.now().isoformat()} | Role: {role} | "
        f"Question: {question} | Response: {result['answer']}"
    )
    with open("interactions.log", "a") as logfile:
        logfile.write(log_entry + "\n")
