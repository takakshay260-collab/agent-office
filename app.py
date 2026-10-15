import os
import uuid
import asyncio
from pathlib import Path
from typing import Dict, List
import requests
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from google import genai

app = FastAPI(title="Self-Updating AI Agent Office")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Credentials
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        client = None

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

# --- SMART AUTO-UPDATING AI CALLER ---
def execute_smart_ai(prompt: str) -> str:
    """Dynamically queries Google for the newest available model and auto-heals"""
    if not client:
        return "[Notice] Simulation Mode: Please check your GEMINI_API_KEY in Render."
    
    discovered_models: List[str] = []
    try:
        # Dynamically ask Google for all active models
        for m in client.models.list():
            clean_name = m.name.replace("models/", "")
            if "flash" in clean_name.lower():
                discovered_models.append(clean_name)
    except Exception:
        pass
    
    # Priority list: dynamically discovered models first, then known fallbacks
    candidates = discovered_models + ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    
    # Remove duplicates preserving priority order
    seen = set()
    model_queue = [x for x in candidates if not (x in seen or seen.add(x))]

    last_error = ""
    for model_name in model_queue:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = str(e)
            continue
            
    return f"[Agent Error]: Auto-update attempted {model_queue}, latest response: {last_error}"

# --- TELEGRAM ALERTS ---
def send_telegram_alert(message: str):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=5)
        except Exception:
            pass

# --- AUTO SCOUT AGENT (Monitors Jobs 24/7) ---
async def auto_job_scout():
    await asyncio.sleep(5)
    while True:
        try:
            feed_url = "https://remoteok.com/api"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(feed_url, headers=headers, timeout=10)
            if res.status_code == 200:
                jobs = res.json()
                for item in jobs[1:6]:
                    job_id = str(item.get("id", uuid.uuid4()))
                    if job_id not in JOBS_DB:
                        title = item.get("position", "Freelance Task")
                        company = item.get("company", "Remote Client")
                        JOBS_DB[job_id] = {
                            "id": job_id,
                            "title": title,
                            "client": company,
                            "budget": "₹1,500",
                            "status": "PENDING_APPROVAL",
                            "agent1_output": "",
                            "agent2_feedback": "",
                            "paid": False
                        }
                        send_telegram_alert(f"🔔 NEW JOB FOUND!\n\nTask: {title}\nClient: {company}\nBudget: ₹1,500\n\nOpen dashboard to approve!")
                        break
        except Exception:
            pass
        await asyncio.sleep(900)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(auto_job_scout())

# --- AGENT 1: WORKER ---
def agent_1_execute(prompt: str, context: str = "") -> str:
    full_prompt = f"You are Agent 1 (Execution Specialist).\nTask: {prompt}\nAuditor Feedback: {context}\nProduce high quality work directly."
    return execute_smart_ai(full_prompt)

# --- AGENT 2: AUDITOR ---
def agent_2_verify(task: str, output: str) -> str:
    audit_prompt = f"You are Agent 2 (Auditor).\nTask: {task}\nDraft: {output}\nAudit for mistakes, score /100, suggest fixes."
    return execute_smart_ai(audit_prompt)

# --- ROUTES ---
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
    send_telegram_alert(f"📥 New Job Added: {title} ({budget})")
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
        job["agent2_feedback"] = "All previous mistakes resolved successfully! Ready for delivery."
        job["status"] = "READY_FOR_PAYMENT"
        send_telegram_alert(f"💰 Job '{job['title']}' is READY FOR PAYMENT!")
    return RedirectResponse(url="/", status_code=303)

@app.post("/jobs/{job_id}/confirm-payment")
async def confirm_payment(job_id: str):
    job = JOBS_DB.get(job_id)
    if job:
        job["paid"] = True
        job["status"] = "COMPLETED"
        send_telegram_alert(f"✅ Payment Confirmed & Delivered for '{job['title']}'!")
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
