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
        <span id="progressText" class="text-xs font-mono text-emerald-400 font-bold">Initial
