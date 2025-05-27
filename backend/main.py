from fastapi import FastAPI, Query
from hr_policy_data import POLICIES
from utils import log_interaction

app = FastAPI(title="HR Policy Assistant", version="1.0.0")


@app.get("/")
def read_root():
    return {"msg": "Welcome to the HR Policy Assistant API"}


@app.get("/ask")
def ask_policy(
    question: str = Query(..., description="Your HR-related question"),
    role: str = Query(..., description="Employee role")
):
    result = next(
        (
            {
                "answer": p["answer"],
                "policy_link": p["link"],
            }
            for p in POLICIES
            if (
                role.lower() in p["roles"] and
                any(word in question.lower() for word in p["keywords"])
            )
        ),
        {"answer": "Sorry, I don't know. Please contact HR."}
    )
    log_interaction(question, role, result)
    return result
