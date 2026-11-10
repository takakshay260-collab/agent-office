from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="Agent Workbench Setup", version="0.2.0")

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#101522">
  <title>Agent Workbench - Setup in progress</title>
  <style>
    :root{color-scheme:dark;font-family:Inter,Segoe UI,Arial,sans-serif;background:#0c111b;color:#edf2f9}
    *{box-sizing:border-box}body{min-height:100vh;margin:0;display:grid;place-items:center;padding:24px;background:radial-gradient(ellipse at 80% 0,#1b2b3d 0,transparent 42%),#0c111b}
    main{width:min(680px,100%);padding:32px;border:1px solid #2b3b50;border-radius:22px;background:#121a27;box-shadow:0 22px 70px #0006}
    .tag{display:inline-block;padding:7px 11px;border:1px solid #655331;border-radius:999px;background:#282316;color:#f2d291;font-size:12px}
    h1{margin:22px 0 12px;font-size:clamp(27px,5vw,40px);letter-spacing:-.04em}
    p{color:#b8c5d6;line-height:1.65}
    .box{margin-top:22px;padding:17px;border:1px solid #304259;border-radius:14px;background:#172130}
    .box b{display:block;margin-bottom:7px;color:#a9c1ff}
    .muted{font-size:13px;color:#91a0b5}
  </style>
</head>
<body>
  <main>
    <span class="tag">Setup in progress</span>
    <h1>Your workroom is being prepared</h1>
    <p>This page is not currently connected to a job marketplace or live AI agents. It does not accept client orders or payments.</p>
    <div class="box"><b>Current status</b><p class="muted">Job search: not connected<br>Live agents: 0<br>Payments: disabled</p></div>
    <p class="muted">Do not send passwords, private client details, or payment information here.</p>
  </main>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def client_portal():
    return HTMLResponse(content=PAGE)


@app.get("/health")
async def health_check():
    return {
        "status": "setup_required",
        "live_agents": 0,
        "job_search": "not_connected",
        "payments": "disabled",
        "time": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/boss", include_in_schema=False)
async def boss_dashboard():
    return JSONResponse(
        {"detail": "Private dashboard disabled until sign-in protection is configured."},
        status_code=404,
    )


@app.post("/api/order")
async def api_order():
    return JSONResponse(
        {"status": "unavailable", "detail": "Order intake is disabled during setup."},
        status_code=503,
    )


@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    return JSONResponse(
        {"status": "not_found", "detail": "There are no live jobs in this service."},
        status_code=404,
    )


@app.post("/api/job/{job_id}/unlock")
async def unlock_job(job_id: str):
    return JSONResponse(
        {"status": "unavailable", "detail": "No payment verification is configured."},
        status_code=503,
    )
