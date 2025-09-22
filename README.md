# GC-AI 

## 실행 방법
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m pipelines.parse_gc samples/g1_unified_gc.log --out data/gc_events.jsonl
python -m pipelines.run_pipeline data/gc_events.jsonl --rules rules/rules.yaml --out data/diagnosis.json

uvicorn api.main:app --reload --port 8000
```

- 웹 규칙 관리 UI: http://127.0.0.1:8000/rules/
