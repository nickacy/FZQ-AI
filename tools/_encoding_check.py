import os

base = os.path.dirname(os.path.abspath(__file__))
targets = [
    os.path.join(base, 'fzq_ai_agent', 'utils'),
    os.path.join(base, 'fzq_ai_agent', 'dashboard', 'pages'),
    os.path.join(base, 'fzq_ai_agent', 'report'),
]

encodings_to_try = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1', 'cp1252']

for d in targets:
    if not os.path.isdir(d):
        continue
    for fname in os.listdir(d):
        if not fname.endswith('.py'):
            continue
        fpath = os.path.join(d, fname)
        detected = None
        for enc in encodings_to_try:
            try:
                with open(fpath, 'r', encoding=enc) as fh:
                    fh.read()
                detected = enc
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        if detected is None:
            print(f'NONE   {fpath}')
        elif detected != 'utf-8':
            print(f'{detected.upper():8s} {fpath}')

struct = os.path.join(base, 'structure.txt')
if os.path.exists(struct):
    detected = None
    for enc in encodings_to_try:
        try:
            with open(struct, 'r', encoding=enc) as fh:
                fh.read()
            detected = enc
            break
        except:
            continue
    if detected is None:
        print(f'NONE   {struct}')
    elif detected != 'utf-8':
        print(f'{detected.upper():8s} {struct}')

print('SCAN_COMPLETE')
