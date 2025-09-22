import argparse, json, yaml
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('events_jsonl')
    ap.add_argument('--rules', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    rows = [json.loads(x) for x in open(args.events_jsonl)]
    df = pd.DataFrame(rows)
    df['ts'] = pd.to_datetime(df['ts']).sort_values()
    df.set_index('ts', inplace=True)
    roll = df['pause_ms'].rolling('10min')
    feats = pd.DataFrame({
        'p95_pause': roll.quantile(0.95),
        'stw_percent': roll.sum()/(10*60*1000)*100
    }).dropna().reset_index()

    rules = yaml.safe_load(open(args.rules))
    out = []
    for _, row in feats.iterrows():
        matches = []
        for r in rules:
            cond = r.get('when',{})
            ok = False
            for c in cond.get('all',[]):
                k,v = list(c.items())[0]; val = row.get(k)
                if v.startswith('>='): ok = val>=float(v[2:])
            if ok: matches.append(r)
        out.append({'win_end': row['ts'].isoformat(), 'p95_pause': row['p95_pause'], 'stw_percent': row['stw_percent'], 'rules': matches})
    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
