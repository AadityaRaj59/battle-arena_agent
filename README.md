# Battle Arena Command Center

A local dashboard for the Innov8 4.0 Battle Arena agent, combining the supplied HTML demo UI with a read-only Python bridge to the agent's checkpoint and decision logs.

## What's included

- `frontend/index.html` — original dashboard UI, with a new **Live Agent** tab.
- `agent.py` and `arena_client.py` — the Python agent and Arena API client.
- `dashboard_server.py` — standard-library local web server that serves the UI and read-only status/state/log endpoints.
- `start-dashboard.ps1` — Windows PowerShell launcher.

## 1. Run the dashboard (no Arena key required)

Open PowerShell in this folder and run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\start-dashboard.ps1
```

Then open **http://127.0.0.1:8765**. The demo pages work without a key. Select **Live Agent** to check for local state. Until the agent has run and written `state/state.json` and `state/decisions.jsonl`, the live section will show that no checkpoint is available.

## 2. Connect it to the Python agent

The dashboard and agent must use the same `STATE_DIR`. The default is `./state` relative to this project directory. The dashboard only reads these local files; it does not invoke the agent or call the Arena API.

If the organisers have issued an Arena key and authorised the agent to run, open a **second PowerShell window** in this project directory:

```powershell
$env:ARENA_URL = "https://innov8-battle-arena.onrender.com"
$env:ARENA_KEY = Read-Host "Paste the authorised Arena key"
$env:STATE_DIR = (Join-Path $PWD "state")
$env:PENALTY_FACTOR = "0.05"
python .\agent.py
```

Set `PENALTY_FACTOR` to the value actually announced by the organisers; `0.05` is only the code's fallback. Keep the agent terminal open. The Live Agent tab can then read its checkpoint and decision log. The key is read from the PowerShell environment and is never displayed by the dashboard. Do not put the key in source code, HTML, `.env` committed to Git, screenshots, or public repositories.

**Important:** `agent.py` is an autonomous agent. Once launched with a valid key it can make metered API calls and submit offers when the Arena phase permits. Do not launch it just to test the UI. The dashboard bridge itself is read-only and does not start or stop the agent.

## 3. Test the Python files

```powershell
python -m py_compile .\agent.py .\arena_client.py .\dashboard_server.py
```

## Publish the static demo on GitHub Pages

1. Push this project to a GitHub repository on the `main` branch.
2. In the repository, open **Settings → Pages** and set the build/deployment source to **GitHub Actions**.
3. The included `.github/workflows/pages.yml` deploys the `frontend/` folder on each push to `main`. Check the repository's **Actions** tab for the deployment URL.
4. GitHub Pages only hosts the static demo UI. Its **Live Agent** tab cannot reach the local Python bridge from a public page, so use the local server for live checkpoint/log data.

## Hosting notes

- The dashboard is intentionally bound to `127.0.0.1` by default. It is for local development, not public hosting.
- GitHub Pages can host the static demo (`frontend/index.html`) but cannot run the Python bridge or read the agent's local files.
- To host a live dashboard remotely, deploy the bridge privately with authentication and HTTPS first. Do not expose this unauthenticated read-only server to the public internet.
