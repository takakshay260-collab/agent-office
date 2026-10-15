import os
import uuid
from pathlib import Path
from typing import Dict
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from google import genai

app = FastAPI(title="AI Agent Office Dashboard")

# Paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Gemini Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

JOBS_DB: Dict[str, dict] = {
    "sample-101": {
        "id": "sample-101",
        "title": "Write 5 LinkedIn Hooks on B2B SaaS Growth",
        "client": "Client_Alpha",
        "budget": "₹1,500",
        "status": "PENDING_APPROVAL",
        "agent1_output": "",
        "agent2_feedback": "",
        "paid": False
    }
}

def agent_1_execute(prompt: str, context: str = "") -> str:
    if not client:
        return "[Simulation Mode] Agent 1 completed draft. Set GEMINI_API_KEY in Render."
    full_prompt = f"You are Agent 1 (Execution Specialist).\nTask: {prompt}\nCorrections: {context}\nComplete the job cleanly."
    response = client.models.generate_content(model="gemini-2.0-flash", contents=full_prompt)
    return response.text

def agent_2_verify(task: str, output: str) -> str:
    if not client:
        return "[Simulation Mode] Agent 2 verified: Structure looks good."
    audit_prompt = f"You are Agent 2 (Auditor).\nTask: {task}\nOutput: {output}\nAudit for flaws, score /100, list corrections."
    response = client.models.generate_content(model="gemini-2.0-flash", contents=audit_prompt)
    return response.text

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"jobs": list(JOBS_DB.values())})

@app.post("/jobs/create")
async def create_job(title: str = Form(...), client_name: str = Form(...), budget: str = Form(...)):
    job_id = str(uuid.uuid4())[:8]
    JOBS_DB[job_id] = {
        "id": job_id, "title": title, "client": client_name, "budget": budget,
        "status": "PENDING_APPROVAL", "agent1_output": "", "agent2_feedback": "", "paid": False
    }
    return RedirectResponse(url="/", status_code=303)

@app.post("/jobs/{job_id}/approve")
async def approve_job(job_id: str):
    job = JOBS_DB.get(job_id)
    if job:
        job["status"] = "WORKING"
        draft = agent_1_execute(job["title"])
        job["agent1_output"] = draft
        job["status"] = "AUDITING"
        feedback = agent_2_verify(job["title"], draft)
        job["agent2_feedback"] = feedback
    return RedirectResponse(url="/", status_code=303)

@app.post("/jobs/{job_id}/one-click-fix")
async def one_click_fix(job_id: str):
    job = JOBS_DB.get(job_id)
    if job:
        improved = agent_1_execute(job["title"], context=job["agent2_feedback"])
        job["agent1_output"] = improved
        job["agent2_feedback"] = "All mistakes resolved! Ready for delivery."
        job["status"] = "READY_FOR_PAYMENT"
    return RedirectResponse(url="/", status_code=303)

@app.post("/jobs/{job_id}/confirm-payment")
async def confirm_payment(job_id: str):
    job = JOBS_DB.get(job_id)
    if job:
        job["paid"] = True
        job["status"] = "COMPLETED"
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
