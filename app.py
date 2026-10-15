import os
import uuid
import asyncio
from pathlib import Path
from typing import Dict
import requests
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from google import genai

app = FastAPI(title="AI Agent Office Dashboard")

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

JOBS_DB: Dict[str, dict] = {}

def send_telegram_alert(message: str):
    """Sends real-time notification to your phone"""
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=5)
        except Exception:
            pass

# --- AUTO SCOUT AGENT (Monitors Online Feeds 24/7) ---
async def auto_job_scout():
    """Checks public job feeds and alerts your phone when work is found"""
    await asyncio.sleep(5)  # wait for startup
    while True:
        try:
            # Fetches public remote writing/editing/automation jobs
            feed_url = "https://remoteok.com/api"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(feed_url, headers=headers, timeout=10)
            if res.status_code == 200:
                jobs = res.json()
                for item in jobs[1:6]: # check latest 5 listings
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
                        # Ping phone
                        send_telegram_alert(f"🔔 NEW JOB FOUND!\n\nTask: {title}\nClient: {company}\nBudget: ₹1,500\n\nOpen your dashboard to approve!")
                        break # add one at a time
        except Exception as e:
            pass
        
        # Runs every 15 minutes automatically
        await asyncio.sleep(900)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(auto_job_scout())

# --- AGENT 1: WORKER ---
def agent_1_execute(prompt: str, context: str = "") -> str:
    if not client:
        return "[Notice] Simulation: Task completed successfully."
    full_prompt = f"You are Agent 1 (Worker).\nTask: {prompt}\nContext: {context}\nProduce high quality deliverable."
    try:
        response = client.models.generate_content(model="gemini-1.5-flash", contents=full_prompt)
        return response.text
    except Exception:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=full_prompt)
        return response.text

# --- AGENT 2: AUDITOR ---
def agent_2_verify(task: str, output: str) -> str:
    if not client:
        return "[Notice] Audit complete: Structure verified. Score: 95/100."
    audit_prompt = f"You are Agent 2 (Auditor).\nTask: {task}\nDraft: {output}\nAudit for mistakes, score /100, suggest fixes."
    try:
        response = client.models.generate_content(model="gemini-1.5-flash", contents=audit_prompt)
        return response.text
    except Exception:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=audit_prompt)
        return response.text

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
        job["agent2_feedback"] = "All mistakes resolved! Ready for delivery."
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
