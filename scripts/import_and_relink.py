#!/usr/bin/env python3
"""Import all workflows into an n8n instance and re-point Execute Workflow nodes.
Usage: N8N_URL=http://localhost:5678 N8N_API_KEY=xxx python3 scripts/import_and_relink.py
The exported files reference workflow IDs from the original instance; this maps them by name."""
import json, glob, os, re, urllib.request
URL = os.environ["N8N_URL"].rstrip("/"); KEY = os.environ["N8N_API_KEY"]
# old instance ID -> workflow prefix (from WF-0's router). PJzQ... is assumed to be WF-8 (CREA).
OLD = {"6T8ubyfWiYVe2Ost":"WF: 2-","MYUy8Jy1YFBMaKbi":"WF: 3-","Hz0Z9EKUX4gvdAeg":"WF: 4-",
       "NMOiutyLXKnBkbUe":"WF: 5-","PBezeZyVChps7OFa":"WF: 6-","Zc9vknjkHhJhRsw0":"WF: 7-",
       "y3ODSCBtBqRwOj09":"WF: 9-","vdwvkG3gMCb046qE":"WF: 1-","HRWfImperiality01":"WF: HR-",
       "PJzQnkkTKbBrEbZK":"WF: 8-"}
def api(method, path, body=None):
    r = urllib.request.Request(URL+"/api/v1"+path, method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"X-N8N-API-KEY":KEY,"Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r))
KEEP = ("name","nodes","connections","settings")
created = {}  # prefix -> (new id, workflow json)
for f in sorted(glob.glob("workflows/*.json")):
    wf = json.load(open(f))
    wf["settings"] = {k:v for k,v in wf.get("settings",{}).items() if k in ("executionOrder",)}
    res = api("POST","/workflows",{k:wf[k] for k in KEEP})
    prefix = re.match(r"(WF: [\w]+-)", wf["name"]).group(1)
    created[prefix] = (res["id"], wf); print("imported", wf["name"][:50], "->", res["id"])
for prefix,(nid,wf) in created.items():
    changed = False
    for n in wf["nodes"]:
        if n["type"].endswith("executeWorkflow"):
            ref = n["parameters"].get("workflowId"); ref = ref if isinstance(ref,str) else ref.get("value","")
            old = re.sub(r'[={}" ]','',ref)
            if old in OLD and OLD[old] in created:
                n["parameters"]["workflowId"] = created[OLD[old]][0]; changed = True
            else: print("!! unresolved Execute Workflow ref in", prefix, n["name"], old)
    if changed:
        api("PUT","/workflows/"+nid,{k:wf[k] for k in KEEP}); print("relinked", prefix)
print("Done. Now: add OpenAI/Gmail/Slack/Sheets credentials in the UI, then activate WF-10 first, then the rest.")
