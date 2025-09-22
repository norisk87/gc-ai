from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
import pandas as pd, io, json, yaml
from sklearn.ensemble import IsolationForest

router = APIRouter(tags=["diagnose"])

def compute_features(df, window='10min'):
    df = df.copy()
    df['ts'] = pd.to_datetime(df['ts'])
    df = df.sort_values('ts').set_index('ts')
    roll = df['pause_ms'].rolling(window)
    feats = pd.DataFrame({
        'p50_pause': roll.quantile(0.5),
        'p95_pause': roll.quantile(0.95),
        'p99_pause': roll.quantile(0.99),
        'stw_percent': roll.sum() / (pd.to_timedelta(window).total_seconds()*1000) * 100
    }).dropna().reset_index().rename(columns={'ts':'win_end'})
    return feats

def apply_rules(features_df, rules):
    results = []
    for _, row in features_df.iterrows():
        fired = []
        for rule in rules:
            cond = rule.get('when', {})
            def check(expr):
                key, cmp = list(expr.items())[0]
                val = row.get(key)
                if pd.isna(val): return False
                s = cmp.strip()
                if s.startswith('>='): return val >= float(s[2:])
                if s.startswith('>'):  return val > float(s[1:])
                if s.startswith('<='): return val <= float(s[2:])
                if s.startswith('<'):  return val < float(s[1:])
                if s.startswith('=='): return val == float(s[2:])
                return False
            if 'all' in cond: ok = all(check(c) for c in cond['all'])
            elif 'any' in cond: ok = any(check(c) for c in cond['any'])
            else: ok = all(check({k:v}) for k,v in cond.items())
            if ok:
                fired.append({'id': rule['id'], 'severity': rule.get('severity','info'), 'advice': rule.get('advice',[])})
        results.append({'win_end': row['win_end'].isoformat(), 'rules': fired})
    return results

@router.post("/diagnose")
async def diagnose(jsonl: str = Body(..., embed=True), rules_yaml: str | None = Body(None, embed=True)):
    lines = [l for l in io.StringIO(jsonl).read().splitlines() if l.strip()]
    events = [json.loads(l) for l in lines]
    df = pd.DataFrame(events)
    feats = compute_features(df)
    X = feats[['p95_pause','stw_percent']].fillna(0.0)
    if len(X) >= 32:
        model = IsolationForest(n_estimators=200, contamination=0.02, random_state=42).fit(X)
        scores = -model.decision_function(X)
    else:
        scores = [0.0]*len(X)
    if rules_yaml:
        rules = yaml.safe_load(rules_yaml)
    else:
        rules = []
    fired = apply_rules(feats, rules)
    out = []
    for i, r in enumerate(fired):
        out.append({
            'win_end': r['win_end'],
            'p50_pause': float(feats.iloc[i]['p50_pause']),
            'p95_pause': float(feats.iloc[i]['p95_pause']),
            'p99_pause': float(feats.iloc[i]['p99_pause']),
            'stw_percent': float(feats.iloc[i]['stw_percent']),
            'anomaly_score': float(scores[i]) if i < len(scores) else 0.0,
            'rules': r['rules']
        })
    return JSONResponse(out)
