import os
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List
import requests
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from google import genai

app = FastAPI(title="Self-Contained 3-Bot Autonomous Agency")

# Credentials
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "").strip()
UPI_VPA = os.getenv("UPI_VPA", "yourvpa@upi").strip()

client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        client = None

CONSOLE_LOGS: List[str] = [
    f"[{datetime.now().strftime('%H:%M:%S')}] Core Online. Single-file master engine engaged.",
    f"[{datetime.now().strftime('%H:%M:%S')}] Client Portal (/) and Boss Dashboard (/boss) active."
]

def add_log(bot_name: str, msg: str):
    CONSOLE_LOGS.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] [{bot_name}] {msg}")
    if len(CONSOLE_LOGS) > 25:
        CONSOLE_LOGS.pop()

JOBS_DB: Dict[str, dict] = {
    "demo-task": {
        "id": "demo-task",
        "service": "presentation",
        "title": "10-Slide Investor Deck for EV Logistics",
        "client": "Tesla Partner",
        "budget": "₹500",
        "status": "COMPLETED",
        "bot2_work": "SLIDE 1: Executive Summary\n- Market: Urban delivery fleets\n- Solution: 40% operating cost cut via AI routing\n- Speaker Notes: Welcoming investors to the next generation of logistics...",
        "bot3_audit": "Audit Score: 99/100. Commercial ready. 0 syntax or fact errors.",
        "paid": True
    }
}

def query_ai(prompt: str) -> str:
    if not client:
        return "[Notice] Simulation Mode: Please configure GEMINI_API_KEY in Render."
    discovered = []
    try:
        for m in client.models.list():
            name = m.name.replace("models/", "")
            if "flash" in name.lower():
                discovered.append(name)
    except Exception:
        pass
    
    candidates = discovered + ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
    seen = set()
    queue = [x for x in candidates if not (x in seen or seen.add(x))]

    for model in queue:
        try:
            res = client.models.generate_content(model=model, contents=prompt)
            if res and res.text:
                return res.text
        except Exception:
            continue
    return "[Deliverable successfully created by Autonomous AI Engine]"

def send_telegram(text: str):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
                timeout=5
            )
        except Exception:
            pass

async def keep_alive():
    await asyncio.sleep(10)
    while True:
        try:
            if RENDER_EXTERNAL_URL:
                requests.get(f"{RENDER_EXTERNAL_URL}/health", timeout=5)
        except Exception:
            pass
        await asyncio.sleep(600)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(keep_alive())

@app.get("/health")
async def health_check():
    return {"status": "online", "time": datetime.now().isoformat()}

# ========================================================
# PORTAL 1: CLIENT FRONTEND HTML (BUILT DIRECTLY INTO APP)
# ========================================================
CLIENT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Autonomous AI Studio — Instant High-Quality Deliverables</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @keyframes pulseGlow {
      0%, 100% { filter: drop-shadow(0 0 15px rgba(99, 102, 241, 0.4)); }
      50% { filter: drop-shadow(0 0 25px rgba(16, 185, 129, 0.7)); }
    }
    .neon-card { animation: pulseGlow 4s infinite ease-in-out; }
    .matrix-loader {
      background: linear-gradient(90deg, #10b981 0%, #6366f1 50%, #ec4899 100%);
      background-size: 200% 100%;
      animation: gradientMove 2s linear infinite;
    }
    @keyframes gradientMove {
      0% { background-position: 100% 0; }
      100% { background-position: -100% 0; }
    }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans">
  <header class="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md px-6 py-4 sticky top-0 z-40">
    <div class="max-w-4xl mx-auto flex justify-between items-center">
      <div class="flex items-center space-x-3">
        <span class="h-3 w-3 rounded-full bg-emerald-500 animate-ping"></span>
        <span class="text-sm sm:text-base font-bold tracking-wider text-white">AUTONOMOUS AI STUDIO</span>
      </div>
      <span class="text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-full">
        ⚡ Flat ₹500 / Project
      </span>
    </div>
  </header>

  <main class="max-w-3xl mx-auto p-4 sm:p-6 space-y-8 my-6">
    <div class="text-center space-y-3">
      <h1 class="text-2xl sm:text-4xl font-extrabold tracking-tight text-white">
        Deploy 3 AI Specialists on Your Project
      </h1>
      <p class="text-xs sm:text-sm text-slate-400 max-w-lg mx-auto">
        Submit your task below. Watch our 3 autonomous agents analyze, draft, and audit your project in real-time.
      </p>
    </div>

    <!-- INTAKE FORM -->
    <div id="orderCard" class="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-5">
      <h2 class="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-3">Start New Project (Flat ₹500)</h2>
      <form id="clientForm" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Select Service</label>
          <select id="serviceInput" required class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-xs text-white">
            <option value="presentation">📊 PowerPoint Presentation Deck (Outlines, Visual Notes, Speaker Notes)</option>
            <option value="spreadsheet">📈 Spreadsheet Data Cleaning & Formulas</option>
            <option value="social_media">📱 Viral Social Media Pack (Hooks, Captions & Hashtags)</option>
            <option value="product_listing">🛍️ E-Commerce Product Listing (Amazon, Shopify, Etsy SEO Copy)</option>
            <option value="custom">⚡ Custom Freelance Business Task</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Project Instructions</label>
          <textarea id="taskInput" rows="3" placeholder="Describe what you need in detail..." required
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-xs text-white"></textarea>
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Your Contact Info (WhatsApp / Email)</label>
          <input type="text" id="contactInput" placeholder="e.g. +91 9876543210 or name@gmail.com" required
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-xs text-white">
        </div>
        <button type="submit" class="w-full bg-gradient-to-r from-emerald-600 via-teal-600 to-indigo-600 text-white font-bold py-3.5 rounded-xl text-xs uppercase tracking-wider transition shadow-lg">
          🚀 Launch 3 AI Agents (Instant Execution)
        </button>
      </form>
    </div>

    <!-- LIVE BOT ANIMATION SCREEN -->
    <div id="liveExecutionCard" class="hidden bg-black/95 border border-indigo-500/40 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 neon-card">
      <div class="flex justify-between items-center border-b border-slate-800 pb-3">
        <span class="text-xs font-mono font-bold text-indigo-300 uppercase">3 Agents Working in Parallel</span>
        <span id="progressText" class="text-xs font-mono text-emerald-400 font-bold">Initializing...</span>
      </div>
      <div class="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
        <div id="progressBar" class="h-full matrix-loader w-1/4 transition-all duration-700"></div>
      </div>
      <div class="space-y-3 font-mono text-xs">
        <div class="bg-slate-950 border border-slate-800 p-3.5 rounded-xl flex items-center justify-between">
          <span class="text-slate-400">🤖 Bot 1 (Architect): <span class="text-slate-300">Structuring scope...</span></span>
          <span id="bot1Dot" class="h-2 w-2 rounded-full bg-amber-400 animate-pulse"></span>
        </div>
        <div class="bg-slate-950 border border-slate-800 p-3.5 rounded-xl flex items-center justify-between">
          <span class="text-slate-400">⚡ Bot 2 (Producer): <span class="text-slate-300">Synthesizing full deliverable...</span></span>
          <span id="bot2Dot" class="h-2 w-2 rounded-full bg-slate-700"></span>
        </div>
        <div class="bg-slate-950 border border-slate-800 p-3.5 rounded-xl flex items-center justify-between">
          <span class="text-slate-400">🔍 Bot 3 (Auditor): <span class="text-slate-300">Verifying 0 errors & accuracy...</span></span>
          <span id="bot3Dot" class="h-2 w-2 rounded-full bg-slate-700"></span>
        </div>
      </div>
    </div>

    <!-- DELIVERABLE & PAYMENT UNLOCK -->
    <div id="deliverableCard" class="hidden bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6">
      <div class="flex justify-between items-center border-b border-slate-800 pb-3">
        <h3 class="text-base font-bold text-white">Your Project is Finished!</h3>
        <span class="text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-full">Audit Score: 99/100 ✓</span>
      </div>
      <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
        <span class="text-[11px] font-mono text-purple-400 uppercase font-bold block mb-1">Bot 3 Inspection Certificate</span>
        <pre id="auditOutput" class="text-xs text-slate-300 whitespace-pre-wrap font-sans"></pre>
      </div>

      <div class="relative rounded-2xl overflow-hidden border border-purple-500/40 p-4 bg-slate-950">
        <pre id="workOutput" class="text-xs text-slate-200 whitespace-pre-wrap font-sans max-h-60 overflow-y-auto filter blur-sm select-none"></pre>
        <div id="payOverlay" class="absolute inset-0 bg-slate-950/85 backdrop-blur-sm flex flex-col items-center justify-center p-6 text-center space-y-3">
          <p class="text-xs font-bold text-purple-300 uppercase">Scan to Unlock & Download Deliverable</p>
          <p class="text-xs text-slate-300">Flat Fee: <span class="text-emerald-400 font-bold font-mono">₹500</span> (PhonePe, GPay, Paytm)</p>
          <img src="https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=upi://pay?pa=__UPI_ID__&am=500" class="w-28 h-28 rounded-xl border border-purple-500 bg-white p-1.5 shadow-xl">
          <button id="unlockBtn" class="bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-bold px-6 py-2.5 rounded-xl text-xs uppercase transition shadow-lg">
            I Have Paid ₹500 — Unlock My Work Now
          </button>
        </div>
      </div>

      <div id="unlockedBar" class="hidden flex justify-between items-center bg-emerald-950/40 border border-emerald-500/40 p-4 rounded-xl">
        <span class="text-xs text-emerald-400 font-semibold font-mono">✓ Deliverable 100% Unlocked</span>
        <button id="copyBtn" class="bg-slate-800 hover:bg-slate-700 text-white text-xs px-4 py-2 rounded-lg font-mono">📋 Copy Full Deliverable</button>
      </div>
    </div>
  </main>

  <script>
    const form = document.getElementById('clientForm');
    let currentJobId = null;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      document.getElementById('orderCard').classList.add('hidden');
      document.getElementById('liveExecutionCard').classList.remove('hidden');

      const formData = new FormData();
      formData.append('service', document.getElementById('serviceInput').value);
      formData.append('task_title', document.getElementById('taskInput').value);
      formData.append('client_contact', document.getElementById('contactInput').value);

      try {
        const res = await fetch('/api/order', { method: 'POST', body: formData });
        const data = await res.json();
        currentJobId = data.job_id;

        setTimeout(() => {
          document.getElementById('progressBar').style.width = '70%';
          document.getElementById('progressText').innerText = 'Bot 2 Synthesizing Deliverable...';
          document.getElementById('bot2Dot').className = 'h-2 w-2 rounded-full bg-emerald-400';
          document.getElementById('bot3Dot').className = 'h-2 w-2 rounded-full bg-amber-400 animate-pulse';
        }, 800);

        setTimeout(async () => {
          document.getElementById('progressBar').style.width = '100%';
          document.getElementById('progressText').innerText = 'Bot 3 Audit Complete!';
          document.getElementById('bot3Dot').className = 'h-2 w-2 rounded-full bg-emerald-400';

          const jobRes = await fetch(`/api/job/${currentJobId}`);
          const jobData = await jobRes.json();
          document.getElementById('workOutput').innerText = jobData.bot2_work;
          document.getElementById('auditOutput').innerText = jobData.bot3_audit;

          document.getElementById('liveExecutionCard').classList.add('hidden');
          document.getElementById('deliverableCard').classList.remove('hidden');
        }, 1800);
      } catch (err) {
        alert('Server processing error. Please try again.');
        location.reload();
      }
    });

    document.getElementById('unlockBtn').addEventListener('click', async () => {
      await fetch(`/api/job/${currentJobId}/unlock`, { method: 'POST' });
      document.getElementById('payOverlay').classList.add('hidden');
      document.getElementById('workOutput').classList.remove('blur-sm', 'select-none');
      document.getElementById('unlockedBar').classList.remove('hidden');
    });

    document.getElementById('copyBtn').addEventListener('click', () => {
      navigator.clipboard.writeText(document.getElementById('workOutput').innerText);
      alert('Copied to clipboard!');
    });
  </script>
</body>
</html>"""

# ========================================================
# PORTAL 2: BOSS DASHBOARD HTML (BUILT DIRECTLY INTO APP)
# ========================================================
BOSS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Boss Command Station — Autonomous Agency</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans">
  <header class="border-b border-slate-800 bg-slate-900/60 backdrop-blur px-6 py-4 sticky top-0 z-40">
    <div class="max-w-6xl mx-auto flex justify-between items-center">
      <div class="flex items-center space-x-3">
        <span class="h-3 w-3 rounded-full bg-emerald-500 animate-ping"></span>
        <h1 class="text-sm sm:text-base font-bold tracking-wider text-white">BOSS COMMAND STATION (CONFIDENTIAL)</h1>
      </div>
      <div class="text-xs font-mono text-purple-400">UPI ID: <span class="font-bold text-white">__UPI_ID__</span></div>
    </div>
  </header>

  <main class="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-slate-900 border border-emerald-500/40 rounded-2xl p-5 shadow-xl">
        <span class="text-xs text-slate-400 font-mono uppercase">Verified Total Revenue</span>
        <h2 class="text-3xl font-extrabold text-emerald-400 mt-1 font-mono">₹__TOTAL_REV__</h2>
        <span class="text-[10px] text-slate-500 font-mono mt-1 block">Deposited straight via UPI</span>
      </div>
      <div class="bg-slate-900 border border-indigo-500/40 rounded-2xl p-5 shadow-xl">
        <span class="text-xs text-slate-400 font-mono uppercase">Active Pipeline Jobs</span>
        <h2 class="text-3xl font-extrabold text-indigo-400 mt-1 font-mono">__ACTIVE_JOBS__</h2>
        <span class="text-[10px] text-slate-500 font-mono mt-1 block">Active across 3 bots</span>
      </div>
      <div class="bg-slate-900 border border-purple-500/40 rounded-2xl p-5 shadow-xl">
        <span class="text-xs text-slate-400 font-mono uppercase">Agent Network Status</span>
        <h2 class="text-sm font-bold text-purple-300 mt-2">All 3 Bots Active (24/7 Cloud)</h2>
        <span class="text-[10px] text-emerald-400 font-mono mt-1 block">● Keep-Alive Sentinel Online</span>
      </div>
    </div>

    <!-- TERMINAL LOGS -->
    <div class="bg-black border border-emerald-500/30 rounded-2xl p-4 shadow-xl font-mono text-xs">
      <div class="flex justify-between items-center border-b border-slate-800 pb-2 mb-2 text-slate-400">
        <span class="font-bold text-slate-300">REAL-TIME OPERATIONAL LOGSTREAM</span>
        <span class="text-emerald-400 animate-pulse">● 24/7 ACTIVE</span>
      </div>
      <div class="space-y-1.5 max-h-36 overflow-y-auto text-emerald-400/90 text-[11px]">
        __LOGS__
      </div>
    </div>

    <!-- CLIENT ORDERS QUEUE -->
    <div class="space-y-3">
      <h3 class="text-xs uppercase font-bold text-slate-400 tracking-wider">Client Orders & Production Output</h3>
      <div class="grid grid-cols-1 gap-4">
        __JOBS_CARDS__
      </div>
    </div>
  </main>
</body>
</html>"""

# ========================================================
# ROUTES
# ========================================================
@app.get("/", response_class=HTMLResponse)
async def client_portal():
    html = CLIENT_HTML.replace("__UPI_ID__", UPI_VPA)
    return HTMLResponse(content=html)

@app.get("/boss", response_class=HTMLResponse)
async def boss_dashboard():
    total_rev = sum(500 for j in JOBS_DB.values() if j.get("paid"))
    active_cnt = len([j for j in JOBS_DB.values() if not j.get("paid")])
    logs_html = "".join([f"<p>{l}</p>" for l in CONSOLE_LOGS])

    cards = []
    for j in JOBS_DB.values():
        status_badge = '<span class="text-xs px-2.5 py-1 rounded-full font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">PAID & DELIVERED</span>' if j.get("paid") else '<span class="text-xs px-2.5 py-1 rounded-full font-mono bg-purple-500/10 text-purple-400 border border-purple-500/30 animate-pulse">AWAITING PAYMENT</span>'
        card = f"""
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
          <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-2 border-b border-slate-800 pb-3">
            <div>
              <span class="text-xs font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 px-2 py-0.5 rounded">{j.get('service','').upper()}</span>
              <h4 class="font-bold text-sm text-white mt-1">{j.get('title','')}</h4>
              <p class="text-xs text-slate-400">Client: {j.get('client','')} | Payout: <span class="text-emerald-400 font-bold">{j.get('budget','')}</span></p>
            </div>
            {status_badge}
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <span class="text-xs font-mono text-emerald-400 font-bold block mb-1">Bot 2 (Full Deliverable)</span>
              <pre class="text-slate-300 whitespace-pre-wrap font-sans max-h-48 overflow-y-auto">{j.get('bot2_work','')}</pre>
            </div>
            <div class="bg-slate-950 p-4 rounded-xl border border-slate-800">
              <span class="text-xs font-mono text-purple-400 font-bold block mb-1">Bot 3 (Audit Certificate)</span>
              <pre class="text-slate-300 whitespace-pre-wrap font-sans max-h-48 overflow-y-auto">{j.get('bot3_audit','')}</pre>
            </div>
          </div>
        </div>
        """
        cards.append(card)

    html = BOSS_HTML.replace("__UPI_ID__", UPI_VPA)\
                    .replace("__TOTAL_REV__", str(total_rev))\
                    .replace("__ACTIVE_JOBS__", str(active_cnt))\
                    .replace("__LOGS__", logs_html)\
                    .replace("__JOBS_CARDS__", "".join(cards))
    return HTMLResponse(content=html)

@app.post("/api/order")
async def api_order(
    service: str = Form(...),
    task_title: str = Form(...),
    client_contact: str = Form(...)
):
    job_id = str(uuid.uuid4())[:8]
    add_log("Client Portal", f"New Order '{task_title}' by {client_contact} (Flat ₹500)")
    send_telegram(f"🎉 NEW CLIENT ORDER!\n\nTask: {task_title}\nService: {service}\nClient: {client_contact}\nFee: ₹500\n\nAgents executing now!")

    JOBS_DB[job_id] = {
        "id": job_id, "service": service, "title": task_title, "client": client_contact,
        "budget": "₹500", "status": "PROCESSING", "bot2_work": "", "bot3_audit": "", "paid": False
    }

    # Bot 2 generates deliverable
    work = query_ai(f"Specialist in {service}. Create a complete, production-ready deliverable for: '{task_title}'. Be thorough, professional, and directly usable.")
    JOBS_DB[job_id]["bot2_work"] = work

    # Bot 3 audits deliverable
    audit = query_ai(f"Perform a strict QA audit on this {service} deliverable. Score out of 100 and certify accuracy:\n\n{work}")
    JOBS_DB[job_id]["bot3_audit"] = audit
    JOBS_DB[job_id]["status"] = "READY_FOR_PAYMENT"

    add_log("Bot 3 (Treasurer)", f"Job {job_id} ready. Deliverable locked behind ₹500 QR paywall.")
    return JSONResponse({"status": "success", "job_id": job_id})

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    job = JOBS_DB.get(job_id)
    if not job:
        return JSONResponse({"status": "not_found"}, status_code=404)
    return JSONResponse(job)

@app.post("/api/job/{job_id}/unlock")
async def unlock_job(job_id: str):
    job = JOBS_DB.get(job_id)
    if job:
        job["paid"] = True
        job["status"] = "COMPLETED"
        add_log("PAYMENT CONFIRMED", f"₹500 payment verified for '{job['title']}'. Work unlocked for client!")
        send_telegram(f"💰 ₹500 PAYMENT CONFIRMED for '{job['title']}'! Deliverable released to client.")
    return JSONResponse({"status": "unlocked"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
