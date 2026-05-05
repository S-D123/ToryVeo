import requests, json
from pathlib import Path

session = requests.Session()

workflow = json.loads(Path('./workflows/comfyui_workflow.json').read_text(encoding="utf-8"))

prompt_node = workflow.get("prompt", {}).get("6")
prompt_node.setdefault("inputs", {})["text"] = "a german car"
print(workflow)
prompt = json.dumps(workflow).encode("utf-8")

res = session.post(
    url="http://127.0.0.1:8188/prompt",
    data=prompt,
    headers={"Content_Type": "application/json"}
)

print(res.status_code)