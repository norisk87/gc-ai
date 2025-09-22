from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import yaml, os

RULES_PATH = os.path.join(os.path.dirname(__file__), "../rules/rules.yaml")
templates = Jinja2Templates(directory="api/templates")

router = APIRouter(prefix="/rules", tags=["rules"])

def load_rules():
    if not os.path.exists(RULES_PATH):
        return []
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []

def save_rules(rules):
    with open(RULES_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(rules, f, allow_unicode=True)

@router.get("/", response_class=HTMLResponse)
async def rules_ui(request: Request):
    rules = load_rules()
    return templates.TemplateResponse("rules.html", {"request": request, "rules": rules})

@router.get("/list")
def list_rules():
    return load_rules()

@router.post("/add")
def add_rule(rule: dict):
    rules = load_rules()
    rules.append(rule)
    save_rules(rules)
    return {"status": "created", "rule": rule}

@router.put("/update/{rule_id}")
def update_rule(rule_id: str, rule: dict):
    rules = load_rules()
    for i, r in enumerate(rules):
        if r.get("id") == rule_id:
            rules[i] = rule
            save_rules(rules)
            return {"status": "updated", "rule": rule}
    raise HTTPException(404, f"rule {rule_id} not found")

@router.delete("/delete/{rule_id}")
def delete_rule(rule_id: str):
    rules = load_rules()
    new_rules = [r for r in rules if r.get("id") != rule_id]
    if len(new_rules) == len(rules):
        raise HTTPException(404, f"rule {rule_id} not found")
    save_rules(new_rules)
    return {"status": "deleted", "rule_id": rule_id}
