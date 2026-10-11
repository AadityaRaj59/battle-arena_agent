# Battle Arena Command Center

Hi, I'm **Aaditya Raj**, a CSE student and the **team leader of Team
Vibranium Coders**. Our team was selected for the **Innov8 4.0 finals at
IIT Delhi**, organised around the Eightfold.ai × ARIES Battle Arena
challenge.

I built this project as part of my work on the finale problem: an
autonomous agent that competes in a live hiring market, along with a
dashboard that helps me inspect its workflow and local decision records.

## Innov8 4.0 Finals --- IIT Delhi

As the leader of Team Vibranium Coders, I worked on our approach to the
Innov8 4.0 finale challenge. Unlike a fixed-file ranking task, the
finale involved a live, shared candidate market where multiple
autonomous agents competed for the same people.

This repository contains the Python agent implementation and a local
command-center dashboard for inspecting the project. The dashboard is a
development and monitoring aid; it does not itself execute the live
agent.

## The finale problem statement

The Innov8 4.0 Battle Arena finale asked us to build an autonomous agent
for a live hiring market with **1,000,000 candidate profiles** and
multiple teams searching the same pool.

The agent needed to:

-   Find candidates who match open requisitions.
-   Decide when search results are enough and when a full profile or
    assessment is worth paying for.
-   Evaluate candidate fit from incomplete and sometimes messy profile
    information.
-   Make offers before other agents sign the same candidates.
-   Track the credit budget and avoid spending when the likely points do
    not justify the cost.

The objective was to earn as many points as possible while keeping
credit use low. The official finale brief defines the arena score as:

`points from candidates held at the end - (credits used × penalty factor)`

The agent is expected to make decisions autonomously during the arena
window. This repository contains my implementation and a supporting
dashboard for the challenge.

## What's in this repository?

-   `agent.py` --- the Python agent and its decision workflow.
-   `arena_client.py` --- the client used to communicate with the Battle
    Arena API.
-   `dashboard_server.py` --- a small local server for the dashboard and
    read-only local state endpoints.
-   `frontend/index.html` --- the dashboard UI.
-   `start-dashboard.ps1` --- starts the dashboard on Windows.
-   `.env.example` --- example environment-variable configuration
    without a real API key.

## How the agent approaches the task

The agent is designed to work through the market in stages:

1.  **Recon and search:** inspect open requisitions and search broadly
    for possible matches.
2.  **Candidate evaluation:** compare skills and role requirements, then
    spend more credits on profiles or assessments only when useful.
3.  **Offer planning:** prioritize stronger candidates and keep
    alternatives available.
4.  **Market and closing decisions:** track the market, available slots,
    and remaining budget, and avoid offers that do not make economic
    sense.

The code saves its checkpoint in `state/state.json` and appends decision
records to `state/decisions.jsonl`, using the configured `STATE_DIR`.

## Dashboard

I also made a local dashboard so I can inspect the project more easily.

The dashboard has sections for:

-   Overview and demo simulation
-   Candidate Explorer
-   Requisition Pipeline
-   Decision Intelligence
-   Activity Logs
-   System Configuration
-   Live Agent status

The demo simulation uses **sample data**. The Live Agent tab reads local
checkpoint and log files through a read-only bridge. The bridge itself
does not call the Arena API, spend credits, or submit offers.

I tested the dashboard locally with sample checkpoint and log files.
That confirms the dashboard can read those files; it does **not** mean
the live Arena agent has been run or verified.

## Run the dashboard on Windows

From the project folder, open PowerShell and run:

``` powershell
.\start-dashboard.ps1
```

Then open:

<http://127.0.0.1:8765>

If PowerShell blocks the script for the current session, run:

``` powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\start-dashboard.ps1
```

To stop the server, press `Ctrl+C` in the PowerShell window where it is
running.

## Configuration and safety

1.  Keep any real `.env` file out of Git.
2.  Set `ARENA_KEY` only when you have an authorized key and are ready
    to run the agent.
3.  The dashboard server and the agent are separate processes.
    Publishing this repository to GitHub does not start the Python agent
    or make the local dashboard bridge available online.
4.  Do not run `agent.py` against the live Arena unless you understand
    that it can make API calls, consume credits, and submit offers.

The local dashboard can be used in demo mode without Arena credentials.

## Current status

-   Dashboard UI: tested locally.
-   Read-only state and log endpoints: tested with local sample files.
-   Live Arena API execution: not verified as part of the dashboard
    test.
-   GitHub Pages: the workflow is included, but deployment still needs
    to be checked in the repository's Actions and Pages settings.

## Project goal

My goal with this project is to build a clear, practical view of the
agent's workflow and make the decision process easier to inspect. I'll
keep improving the agent, its evaluation logic, and the dashboard as I
test more of the system.

------------------------------------------------------------------------

**Author:** Aaditya Raj\
**Role:** Team Leader, Vibranium Coders\
**Finale:** Innov8 4.0 --- IIT Delhi\
**Challenge:** Eightfold.ai × ARIES Battle Arena
