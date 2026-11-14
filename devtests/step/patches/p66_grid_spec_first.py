# ➕🎚️ patch 66 (engines · ➕ plus and 🎚️ range) — found while examining the plus bot (the owner, 14-11: «افحص البوت البلس كليا اشك فيه
#   مشاكل»): a new bot laid its first ladder (4 buys + 4 sells) BEFORE it read the coin's price step from OKX — the step was read only
#   in the loop's reconcile block, a few seconds later. On a coin whose step is 0.01 (SOL · most coins) the first prices went out with
#   4 decimals (79.5229) ⇒ OKX refused them all («Parameter px error» — an alert line on every new bot) and the ladder was re-laid
#   only later by the gap check. The 🪜 step and the DCA engines already read it first thing; now these two do too (a public read,
#   no key · if OKX does not answer, the old fallback stands and the loop reads it later, as before).
#   The sacred ♾️ engine (main.py) has the same order — not touched here (rule: only with the owner's yes).
#   python3 devtests/step/patches/p66_grid_spec_first.py devtests/step/eng/grid_plus.py devtests/step/eng/grid_range.py
import sys

R = [
    ('''    backup_state(STATE_FILE, BACKUP_DIR)
    
    if (not state.get("limit_buys") and not state.get("limit_sells")) or _ini_open():''',
     '''    backup_state(STATE_FILE, BACKUP_DIR)
    load_instrument_spec(config["symbol"])                # 📐 v3.36.44: خطوة السعر والكمية قبل أول سلّم (كان يقراها بعده ⇒ 79.5229 بعملة خطوتها 0.01 ⇒ رفض)
    
    if (not state.get("limit_buys") and not state.get("limit_sells")) or _ini_open():'''),
]

if __name__ == "__main__":
    for p in sys.argv[1:]:
        s = open(p, encoding="utf-8").read()
        for i, (a, b) in enumerate(R):
            if s.count(a) != 1:
                print(f"❌ {p}: replacement {i} found {s.count(a)} times — nothing written"); sys.exit(1)
            s = s.replace(a, b)
        compile(s, p, "exec")
        open(p, "w", encoding="utf-8").write(s)
        print(f"✅ {len(R)} replacement(s) · compiles · {p}")
