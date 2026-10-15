
  import os
import uuid
from pathlib import Path
from typing import Dict
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from google import genai

app = FastAPI(title="AI Agent Office Dashboard")

# Robust directory path resolution
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Configure Gemini Client from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# In-memory storage for tasks
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

# --- AGENT 1: DOER / GENERATOR ---
def agent_1_execute(prompt: str, context: str = "") -> str:
    if not client:
        return "[Simulation Mode] Agent 1 completed the draft. Please provide a valid GEMINI_API_KEY."
    
    full_prompt = f"""You are Agent 1 (Execution Specialist).
Task: {prompt}
Additional Context or Corrections from Auditor: {context}

Execute the job cleanly, professionally, and accurately."""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_prompt
    )
    return response.text

# --- AGENT 2: AUDITOR / QUALITY CHECKER ---
def agent_2_verify(task: str, output: str) -> str:
    if not client:
        return "[Simulation Mode] Agent 2 verified: Structure looks good. No major factual errors found."
    
    audit_prompt = f"""You are Agent 2 (Quality Assurance Auditor).
Client's Original Task: {task}
Agent 1's Work Output: {output}

Your Job:
1. Identify all flaws, factual errors, weak formatting, or missed requirements.
2. Provide a score out of 100.
3. List explicit step-by-step corrections needed."""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=audit_prompt
    )
    return response.text

# --- ROUTES ---
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    # Compatible with newest FastAPI / Starlette signature
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"jobs": list(JOBS_DB.values())}
    )

@app.post("/jobs/create")
async def create_job(title: str = Form(...), client_name: str = Form(...), budget: str = Form(...)):
    job_id = str(uuid.uuid4())[:8]
    JOBS_DB[job_id] = {
        "id": job_id,
        "title": title,
        "client": client_name,
        "budget": budget,
        "status": "PENDING_APPROVAL",
        "agent1_output": "",
        "agent2_feedback": "",
        "paid": False
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
        improved_draft = agent_1_execute(job["title"], context=job["agent2_feedback"])
        job["agent1_output"] = improved_draft
        job["agent2_feedback"] = "All previous mistakes resolved successfully! Ready for delivery."
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
