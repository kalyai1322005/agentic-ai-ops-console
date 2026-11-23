# Agentic AI Ops Console – n8n workflows

12 n8n workflows forming a governed multi-agent system. Every action passes through **WF-10 (Global Guardrail)** before execution.

| Step | Workflow | Role |
|---|---|---|
| 12 | WF-0 CEO Orchestrator | Webhook `/ceo-orchestrator`; classifies request, calls WF-10, routes to departments |
| 01 | WF-10 Global Guardrail | Webhook `/wf10-decision-contract`; approves/blocks, circuit breaker, decision ledger |
| 02 | WF-8 CREA | Risk, ethics and compliance agents |
| 03 | WF-9 Infrastructure | Infra observer, sends signals to WF-10 |
| 04-09, 11, 10 | WF-2 Finance, WF-3 Ops, WF-4 R&D, WF-5 Marketing, WF-6 Sales, WF-7 CX, WF-1 Strategy, WF-HR | Department workflows |

## Deploy (free, self-hosted)
1. `docker compose up -d`, open http://localhost:5678, create the owner account.
2. Settings > n8n API > create an API key.
3. `N8N_URL=http://localhost:5678 N8N_API_KEY=... python3 scripts/import_and_relink.py`
   (imports all 12 and re-points the Execute Workflow nodes to the new IDs).
4. Add credentials in the UI: OpenAI (or n8n free credits), Gmail, Slack, Google Sheets. Gemini for WF-5.
5. Edit WF-10 "Workflow Configuration": `founderEmail`, `opsSlackChannel`, `n8nApiKey`.
6. Publish **WF-10 first**, then WF-8, WF-9, departments, and WF-0 last.
7. Test: `curl -X POST http://localhost:5678/webhook/ceo-orchestrator -H 'Content-Type: application/json' -d '{"request":"Review Q4 budget","mode":"simulation"}'`

## Known issues found in review (not yet fixed)
- **Contract mismatch:** WF-HR and WF-8 send WF-10 `{workflow_source, payload...}`, but WF-10 requires `source_workflow, department, task_type, confidence, founder_available, crea_status, failure_count, audit`. WF-10's schema check will halt them. WF-0 sends the full contract and is fine.
- **WF-9 -> WF-10** uses Execute Workflow, but WF-10 only has a webhook trigger. Switch WF-9 to an HTTP call.
- WF-10 gate sends `confidence` as 0-1 but several workflows default `confidence_score` to 85 (0-100 scale).
- WF-10 "Block: Simulation Mode" means every `mode: simulation` request is blocked by design; use `mode: execute` with confidence >= 0.9 to pass the gate.
- WF-0 departments are hard-wired to `localhost:5678`; change the URL if n8n runs elsewhere.
- WF-10 contains a personal founder email; replace before sharing.
