import argparse, json
from pathlib import Path
from parsers.unified import parse_line

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('logfile')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cnt = 0
    with open(args.logfile, 'r', encoding='utf-8') as f, open(out, 'w', encoding='utf-8') as w:
        for line in f:
            ev = parse_line(line)
            if ev and ev.get('pause_ms') is not None:
                w.write(json.dumps(ev) + '\n')
                cnt += 1
    print(f'wrote {cnt} events to {out}')

if __name__ == '__main__':
    main()
