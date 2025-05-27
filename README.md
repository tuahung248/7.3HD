# HR Policy Assistant Backend

A FastAPI service that answers HR policy questions based on employee role and question context.

## Features

- GET `/ask`: Ask HR questions and receive answers by role (full-time, part-time, contractor).
- Realistic HR policy responses (customize for your organization).
- Logging of all Q&A for monitoring/demo.

## Getting Started

1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2. Run locally:

    ```bash
    uvicorn main:app --reload
    ```

3. API Example:

    ```
    GET http://127.0.0.1:8000/ask?question=Do I get annual leave?&role=full-time
    ```

4. Run tests:

    ```bash
    pytest test_app.py
    ```

5. Docker build and run:

    ```bash
    docker build -t hr-policy-assistant .
    docker run -p 8000:8000 hr-policy-assistant
    ```

## File Structure

- `main.py` – API logic
- `hr_policy_data.py` – Policy knowledge base
- `utils.py` – Logging
- `test_app.py` – Automated tests
- `requirements.txt` – Python dependencies
- `Dockerfile` – Containerization
- `.gitignore` – Ignore build/log files

## Ready for CI/CD

Integrates seamlessly with Jenkins or GitHub Actions for:
- Build, Test, Code Quality, Security Scan, Deploy, Monitoring

---
