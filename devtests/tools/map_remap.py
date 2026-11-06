# remap dashboard line numbers in MAP.md from an old dashboard to the new one; regenerate the function index
#   (rebuilt 2026-11-06 after the scratchpad was lost: lines 1-12 and 20-60 are the original's, 13-19 rebuilt and checked against git history)
import ast, re, difflib, sys, subprocess
old_path, new_path = sys.argv[1], sys.argv[2]
old=open(old_path,encoding="utf-8").read().split("\n"); new=open(new_path,encoding="utf-8").read().split("\n")
sm=difflib.SequenceMatcher(None, old, new, autojunk=False); mp={}
for tag,i1,i2,j1,j2 in sm.get_opcodes():
    if tag=="equal":
        for k in range(i2-i1): mp[i1+k+1]=j1+k+1
def remap(n):
    n=int(n)
    if n in mp: return mp[n]
    k=n
    while k>0 and k not in mp: k-=1
    return mp[k]+(n-k) if k in mp else n
first=1
M=open("MAP.md",encoding="utf-8").read().split("\n")
allfn={}
for m in ast.walk(ast.parse("\n".join(new))):
    if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
        doc=(ast.get_docstring(m) or "").strip().split("\n")[0][:100].replace("|","\\|").replace("\x00","\\0")
        allfn.setdefault(m.name,[]).append((m.lineno,doc))
i0=next(i for i,l in enumerate(M) if l.startswith("## كل دوال اللوحة"))
i1=next(i for i in range(i0+1,len(M)) if M[i].startswith("## ١ · التقسيم العام"))
prev=[re.match(r"\| \d+ \| `([^`]+)`",l).group(1) for l in M[i0+3:i1] if re.match(r"\| \d+ \| `",l)]
extra=[x for x in sys.argv[3:]]
from collections import Counter
want=Counter(prev); [want.update([x]) for x in extra if x not in want]
rows=[]; cnt=Counter()
for nm in want:
    for ln,doc in allfn.get(nm,[]):
        if cnt[nm]<want[nm]: rows.append((ln,nm,doc)); cnt[nm]+=1
rows.sort()
block=[f"## كل دوال اللوحة ({len(rows)})","| السطر | الدالة | الوصف |","|---|---|---|"]+[f"| {a} | `{b}` | {c} |" for a,b,c in rows]+[""]
M=M[:i0]+block+M[i1:]
keys=("لانهائي س","نطاق س","بلس س","main.py","main_range","main_plus","dca.py","dca_buy.py","reinvest.py","| بيعي |","| الاسم | بيعي")
res=[]; skip=False; tbl=False; eng=False; ch=0
for l in M:
    if l.startswith("## "):
        skip=("reinvest.py" in l) or ("المحركات بس" in l) or l.startswith("## كل دوال اللوحة"); tbl=False; eng=False
    if l.startswith("| السطر | الاسم | الدور |") or l.startswith("| الأسطر | القسم |"): tbl=True; eng=False
    elif l.startswith("| الاسم |"): tbl=False; eng=True
    elif l.strip()=="": tbl=False; eng=False
    if not skip and tbl and re.match(r"\| [\d ·\-]+ \|", l) and not any(k in l for k in keys):
        cell=l.split("|")[1]; nc=re.sub(r"\d+", lambda m: str(remap(m.group(0))) if int(m.group(0))>=first else m.group(0), cell)
        if nc!=cell: ch+=1; l="|"+nc+"|"+"|".join(l.split("|")[2:])
    if not skip and not tbl and not eng and re.search(r"س\d{3,5}", l) and not any(k in l for k in keys):
        l2=re.sub(r"س(\d{3,5})", lambda m: "س"+(str(remap(m.group(1))) if int(m.group(1))>=first else m.group(1)), l)
        if l2!=l: ch+=1; l=l2
    res.append(l)
open("MAP.md","w",encoding="utf-8").write("\n".join(res)); print("remapped", ch, "functions", len(rows))
