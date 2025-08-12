import pandas as pd
import re
from collections import defaultdict
from typing import Optional, List, Tuple

# --- 0) Load & normalize 2024 regular season ---
pbp = (
    pd.read_csv('pbp_2024.csv')
      .rename(columns=str.lower)
      .assign(
          gamedate=lambda df: pd.to_datetime(df['gamedate'], errors='coerce'),
          playtype=lambda df: df['playtype'].fillna('').str.lower(),
          description=lambda df: df['description'].fillna('')
      )
      .query("gamedate >= '2024-09-01' and gamedate <= '2025-01-08'")
)

# normalize booleans (feeds can be 0/1/True/False/NaN; ensure missing cols exist)
def b(x):
    return bool(x) if pd.notna(x) else False

for col in [
    'ispass','isrush','isincomplete','issack','istouchdown',
    'isinterception','isfumble','isnoplay',
    'ispenalty','ispenaltyaccepted'
]:
    if col in pbp.columns:
        pbp[col] = pbp[col].map(b)
    else:
        pbp[col] = False

# 'isplay' optional in some feeds; assume True if missing
pbp['isplay'] = pbp['isplay'].map(b) if 'isplay' in pbp.columns else True

# ======================================================================
#               DISAMBIGUATION + TAG PATTERNS
# ======================================================================

TAG_RE_FULL = r'\b(?P<num>\d+)-(?P<name_full>[A-Z][A-Z\.\'\-]+)\b'        # e.g., 17-J.ALLEN
TAG_RE_NAME_ONLY = r'\b(?P<name_only>[A-Z]\.[A-Z][A-Z\.\'\-]+)\b'         # e.g., J.ALLEN

# Unified alternation that avoids duplicate group names
ALT_TAG = (
    r'(?:(?P<num>\d+)-(?P<name_full>[A-Z][A-Z\.\'\-]+)|'
    r'(?P<name_only>[A-Z]\.[A-Z][A-Z\.\'\-]+))'
)

# Optional team prefix sometimes before the tag (e.g., "TO ARI-10-J.DOE" or "TO SF J.DOE")
TEAM_PREFIX = r'(?:(?P<team>[A-Z]{2,3})[-\s])?'
AFTER_TO_TARGET = TEAM_PREFIX + ALT_TAG

def match_name(m) -> Optional[str]:
    if not m:
        return None
    gd = m.groupdict()
    return gd.get('name_full') if gd.get('name_full') is not None else gd.get('name_only')

def pkey(player_name: str, team: Optional[str]):
    return (player_name, team if team else None)

# --- helpers --------------------------------------------------------------
def post_desc(desc: str) -> str:
    m = re.search(r'REVERSED\.(.*)', desc, flags=re.I|re.S)
    return m.group(1) if m else desc

def is_two_point(d: str, row) -> bool:
    if str(row.get('playtype', '')).strip().lower() == 'two-point conversion':
        return True
    return 'TWO-POINT CONVERSION' in d.upper()

def td_in_text_after_review(desc_after_reverse: str) -> bool:
    return bool(re.search(r'\bTOUCHDOWN\b', desc_after_reverse, flags=re.I))

def is_nullified(row, d: str) -> bool:
    """
    Skip only true no-plays: explicit 'NO PLAY', 'NULLIFIED', or offsetting penalties.
    Accepted penalties that *do not* nullify the play should still count for stats.
    """
    u = d.upper()
    if row.get('isnoplay', False):
        return True
    if ' NO PLAY' in u or 'NULLIFIED' in u:
        return True
    if 'OFFSETTING PENALTIES' in u or 'PENALTIES OFFSET' in u or 'PENALTIES ARE OFFSETTING' in u:
        return True
    return False

def passer_name(d: str) -> Optional[str]:
    m = re.search(r'\b' + ALT_TAG + r'\s+PASS\b', d, flags=re.I)
    return match_name(m)

def has_lateral_seq_to_td(d: str) -> bool:
    return bool(re.search(r'PASS.*?(LATERAL|PITCH|BACKWARD PASS).*?TOUCHDOWN', d, flags=re.I|re.S))

def fumble_recovery_scorer(d: str) -> Optional[Tuple[str, Optional[str]]]:
    m = re.search(r'RECOVERED BY\s+(?P<team>[A-Z]{2,3})-' + TAG_RE_FULL + r'.*TOUCHDOWN', d, flags=re.I|re.S)
    if not m:
        return None
    name = m.group('name_full')
    team = m.group('team').upper()
    return (name, team)

def defense_recovered(d: str, offense: Optional[str]) -> bool:
    m = re.search(r'RECOVERED BY\s+([A-Z]{2,3})-', d, flags=re.I)
    return bool(m and m.group(1).upper() != (offense or '').upper())

def is_text_rush(d: str) -> bool:
    u = d.upper()
    if 'PASS' in u and 'SCRAMBLE' not in u:
        return False
    return (
        'SCRAMBLE' in u
        or 'KNEEL' in u
        or 'DIRECT SNAP' in u
        or bool(re.search(r'\b(LEFT|RIGHT|UP THE MIDDLE|RIGHT GUARD|LEFT GUARD|RIGHT TACKLE|LEFT TACKLE)\b', u))
    )

def penalty_accepted_like_text(desc: str) -> bool:
    """
    Heuristic: penalty is effectively accepted if prose has 'PENALTY ON' or 'ENFORCED AT'
    without 'DECLINED', 'OFFSETTING', or 'NO PLAY'. This covers add-on or enforcement changes.
    """
    u = desc.upper()
    if 'PENALTY' not in u:
        return False
    if ('DECLINED' in u) or ('OFFSETTING' in u) or ('PENALTIES OFFSET' in u) or (' NO PLAY' in u):
        return False
    return ('PENALTY ON' in u) or ('ENFORCED AT' in u)

# ---- Target helpers -------------------------------------------------------
def target_name(desc: str) -> Optional[str]:
    """
    Intended receiver for any pass:
      1) 'INTENDED FOR <name>'
      2) 'PASS ... TO <name>'
      3) fallback 'TO <name>'
    """
    m = re.search(r'\bINTENDED\s+FOR\s+' + AFTER_TO_TARGET, desc, flags=re.I)
    if m:
        return match_name(m)
    m = re.search(r'PASS.*?\bTO\s+' + AFTER_TO_TARGET, desc, flags=re.I | re.S)
    if m:
        return match_name(m)
    m = re.search(r'\bTO\s+' + AFTER_TO_TARGET, desc, flags=re.I)
    return match_name(m) if m else None

def initial_receiver_name(desc: str) -> Optional[str]:
    """
    For a completed pass, return the first receiver (before any laterals).
    """
    u = desc.upper()
    lat = re.search(r'\bLATERAL\s+TO\s+', u, flags=re.I)
    pre = desc if not lat else desc[:lat.start()]
    m = re.search(r'PASS.*?\bTO\s+' + AFTER_TO_TARGET, pre, flags=re.I | re.S)
    if not m:
        m = re.search(r'\bTO\s+' + AFTER_TO_TARGET, pre, flags=re.I)
    return match_name(m) if m else None

# ---- Rush helpers ---------------------------------------------------------
def rush_td_scorer_name(desc: str) -> Optional[str]:
    m = re.search(r'(?P<clause>.*?\bFOR\s+-?\d+\s+YARDS?\b.*?\bTOUCHDOWN\b)', desc, flags=re.I | re.S)
    if not m:
        return None
    clause = m.group('clause')
    last = None
    for mm in re.finditer(ALT_TAG, clause):
        last = match_name(mm)
    return last

def last_tag_name_before_touchdown(desc: str) -> Optional[str]:
    u = desc.upper()
    td_idx = u.find('TOUCHDOWN')
    if td_idx == -1:
        td_idx = len(desc)
    last = None
    for m in re.finditer(ALT_TAG, desc):
        if m.end() <= td_idx:
            last = match_name(m)
        else:
            break
    return last

def rush_carrier_name(desc: str) -> Optional[str]:
    """
    For non-TD runs, grab the first tag in the main clause (strip parens; stop at FUMBLES/PENALTY).
    """
    pre = re.split(r'\bFUMBLES\b|\bPENALTY\b', desc, maxsplit=1, flags=re.I)[0]
    pre = re.sub(r'\([^)]*\)', '', pre)
    m = re.search(ALT_TAG, pre, flags=re.I)
    return match_name(m) if m else None

# ---- Receiving helpers ----------------------------------------------------
def parse_receiving_segments(desc: str, total_yards: int) -> List[Tuple[str, int]]:
    """
    Parse a completed pass into receiving segments (names only) and force their sum to official total_yards.
    """
    u = desc.upper()
    segs: List[List[Optional[int]]] = []

    # Split at first LATERAL to isolate initial catch clause
    lat_match = re.search(r'\bLATERAL\s+TO\s+', u, flags=re.I)
    pre = desc if not lat_match else desc[:lat_match.start()]
    post = '' if not lat_match else desc[lat_match.start():]

    # Initial catch
    m_tag = re.search(r'PASS.*?\bTO\s+' + AFTER_TO_TARGET, pre, flags=re.I | re.S)
    if not m_tag:
        m_tag = re.search(r'\bTO\s+' + AFTER_TO_TARGET, pre, flags=re.I | re.S)
    init_name = match_name(m_tag) if m_tag else None

    init_y = None
    m_yds = re.search(r'\bFOR\s+(-?\d+)\s+YARDS?\b', pre, flags=re.I)
    if not m_yds:
        m_loss = re.search(r'\b(?:FOR A )?LOSS OF\s+(\d+)\s+YARDS?\b', pre, flags=re.I)
        if m_loss:
            init_y = -int(m_loss.group(1))
    if init_y is None and m_yds:
        init_y = int(m_yds.group(1))
    elif init_y is None and re.search(r'\bNO GAIN\b', pre, flags=re.I):
        init_y = 0

    if init_name is not None:
        segs.append([init_name, init_y])

    # Laterals
    for lm in re.finditer(
        r'\bLATERAL\s+TO\s+' + AFTER_TO_TARGET + r'(.*?)(?=\bLATERAL\s+TO\b|\bTOUCHDOWN\b|$)',
        post, flags=re.I | re.S
    ):
        lname = match_name(lm)
        clause = lm.group(0)
        ly = None
        m_yd = re.search(r'\bFOR\s+(-?\d+)\s+YARDS?\b', clause, flags=re.I)
        if not m_yd:
            m_loss = re.search(r'\b(?:FOR A )?LOSS OF\s+(\d+)\s+YARDS?\b', clause, flags=re.I)
            if m_loss:
                ly = -int(m_loss.group(1))
        if ly is None and m_yd:
            ly = int(m_yd.group(1))
        elif ly is None and re.search(r'\bNO GAIN\b', clause, flags=re.I):
            ly = 0
        segs.append([lname, ly])

    # Back-fill any missing yards so that sum(segments) == total_yards
    if segs:
        known_sum = sum(y for _, y in segs if y is not None)
        missing_idxs = [i for i, (_, y) in enumerate(segs) if y is None]
        if missing_idxs:
            remainder = int(total_yards or 0) - known_sum
            segs[missing_idxs[-1]][1] = remainder

    # ENFORCE: segment sum must equal official total_yards (adjust last segment)
    if segs:
        cur_sum = sum(y for _, y in segs if y is not None)
        diff = int(total_yards or 0) - cur_sum
        if diff != 0:
            segs[-1][1] = (segs[-1][1] or 0) + diff

    # Fallback: if we never parsed yards, give all to the initial receiver
    if segs and all(y is None for _, y in segs):
        segs[0][1] = int(total_yards or 0)

    return [(name, int(y)) for name, y in segs if name is not None and y is not None]

def last_receiver_name_before_td(desc: str) -> Optional[str]:
    u = desc.upper()
    td_idx = u.find('TOUCHDOWN')
    if td_idx == -1:
        td_idx = len(desc)
    last = None
    for m in re.finditer(r'\b(?:TO|LATERAL\s+TO)\s+' + AFTER_TO_TARGET, desc, flags=re.I):
        if m.end() <= td_idx:
            last = match_name(m)
        else:
            break
    return last

# =========================
# YARDAGE DIAGNOSTICS
# =========================
yard_issues = []

def last_numeric_yards_in_text_before(desc: str, stop_word: str = 'TOUCHDOWN') -> Optional[int]:
    u = desc.upper()
    stop = u.find(stop_word)
    if stop == -1:
        stop = len(desc)
    last_val = None
    for m in re.finditer(r'\bFOR\s+(-?\d+)\s+YARDS?\b', desc, flags=re.I):
        if m.end() <= stop:
            last_val = int(m.group(1))
        else:
            break
    for m in re.finditer(r'\b(?:FOR A )?LOSS OF\s+(\d+)\s+YARDS?\b', desc, flags=re.I):
        if m.end() <= stop:
            last_val = -int(m.group(1))
        else:
            break
    for m in re.finditer(r'\bNO GAIN\b', desc, flags=re.I):
        if m.end() <= stop:
            last_val = 0 if last_val is None else last_val
        else:
            break
    return last_val

STOP_WORDS_RUSH = ('FUMBLES', 'LATERAL', 'PENALTY', 'TOUCHDOWN')

def extract_yards_clause(text: str) -> Optional[int]:
    """Parse 'FOR X YARDS' / 'LOSS OF X' / 'NO GAIN' from a clause."""
    m = re.search(r'\bFOR\s+(-?\d+)\s+YARDS?\b', text, flags=re.I)
    if m: return int(m.group(1))
    m = re.search(r'\b(?:FOR A )?LOSS OF\s+(\d+)\s+YARDS?\b', text, flags=re.I)
    if m: return -int(m.group(1))
    if re.search(r'\bNO GAIN\b', text, flags=re.I): return 0
    return None

def first_segment_yards(desc: str) -> Optional[int]:
    """Yards for the initial ball carrier up to the first post-run event."""
    u = desc.upper()
    stop_idx = min([u.find(w) for w in STOP_WORDS_RUSH if w in u] or [-1])
    pre = desc if stop_idx == -1 else desc[:stop_idx]
    return extract_yards_clause(pre)

def rush_segments(desc: str, official_yards: int, offense_team: Optional[str]) -> List[Tuple[str,int]]:
    """
    Split rushing yards across segments:
      - initial carrier: yards up to first event (fumble/lateral/penalty/TD)
      - offense recoverer(s): their advance yards (if any)
      - reconcile to official only when offense recovers (not defense)
    """
    segs: List[Tuple[str,int]] = []
    carrier = rush_carrier_name(desc)
    if not carrier:
        return segs

    # initial segment
    y0 = first_segment_yards(desc)
    if y0 is None:
        # If no events at all, credit official to carrier and return
        if not any(w in desc.upper() for w in STOP_WORDS_RUSH):
            return [(carrier, int(official_yards))]
        y0 = 0
    segs.append((carrier, int(y0)))

    # offense recoveries and their advances
    for m in re.finditer(
        r'RECOVERED BY\s+(?P<team>[A-Z]{2,3})-' + TAG_RE_FULL + r'(.*?)(?=(RECOVERED BY|TOUCHDOWN|$))',
        desc, flags=re.I|re.S
    ):
        team = m.group('team').upper()
        if offense_team and team == offense_team:
            name = m.group('name_full')
            clause = m.group(0)
            y = extract_yards_clause(clause)
            segs.append((name, int(y) if y is not None else 0))

    # If offense recovered (i.e., multiple segments), reconcile to official total on last offense segment
    if len(segs) >= 2:
        current = sum(y for _, y in segs)
        remainder = int(official_yards) - current
        if remainder != 0:
            segs[-1] = (segs[-1][0], segs[-1][1] + remainder)

    return segs

# =========================
# STATS AGGREGATORS (season + per-game)
# =========================
def empty_stats():
    return {
        'pass_yds': 0, 'pass_td': 0, 'ints': 0,
        'rush_yds': 0, 'rush_td': 0,
        'rec_yds': 0, 'rec_td': 0,
        'fumbles': 0,
        'targets': 0,
        'receptions': 0,
    }

# season totals at (player_name, team_code)
stats = defaultdict(empty_stats)
# per-game totals at (player_name, team_code, game_id)
stats_game = defaultdict(empty_stats)

def add(dct, key, field, val):
    dct[key][field] += val

# =========================
# MAIN LOOP (TD logic same as your baseline; adds targets + receptions)
# =========================
for idx, r in pbp.iterrows():
    d0 = r['description'] or ''
    d = post_desc(d0)
    off = (r.get('offenseteam') or '').upper() or None
    gid = r.get('gameid')

    # skip no-plays and 2-pt
    if is_nullified(r, d):
        continue
    if is_two_point(d, r):
        continue

    td_after = td_in_text_after_review(d)

    # --- INTERCEPTIONS (count INTs; no yards) ---
    if 'INTERCEPT' in d.upper() and (r['ispass'] or 'PASS' in d.upper()):
        pname = passer_name(d)
        if pname:
            add(stats, (pname, off), 'ints', 1)
            add(stats_game, (pname, off, gid), 'ints', 1)

    # --- PASSING yards / TDs (completed forward pass only) ---
    if r['ispass'] and not r['issack'] and not r['isincomplete'] and not r['isinterception']:
        pname = passer_name(d)
        if pname:
            yds_total = int(r['yards']) if pd.notna(r.get('yards')) else 0
            add(stats, (pname, off), 'pass_yds', yds_total)
            add(stats_game, (pname, off, gid), 'pass_yds', yds_total)
            if td_after:
                add(stats, (pname, off), 'pass_td', 1)
                add(stats_game, (pname, off, gid), 'pass_td', 1)

        # receiving segments unchanged
        segments = parse_receiving_segments(d, int(r['yards']) if pd.notna(r.get('yards')) else 0)
        for rname, y in segments:
            add(stats, (rname, off), 'rec_yds', y)
            add(stats_game, (rname, off, gid), 'rec_yds', y)
        if td_after:
            rec_name = last_receiver_name_before_td(d)
            if rec_name:
                if 'FUMBLES' in d.upper() and 'RECOVERED BY' in d.upper():
                    fr = fumble_recovery_scorer(d)
                    if fr and fr[0] == rec_name and (fr[1] == off or fr[1] is None):
                        add(stats, (rec_name, off), 'rec_td', 1)
                        add(stats_game, (rec_name, off, gid), 'rec_td', 1)
                else:
                    add(stats, (rec_name, off), 'rec_td', 1)
                    add(stats_game, (rec_name, off, gid), 'rec_td', 1)

        # receptions: exactly one per completed pass to the initial receiver
        init_rec = initial_receiver_name(d)
        if init_rec:
            add(stats, (init_rec, off), 'receptions', 1)
            add(stats_game, (init_rec, off, gid), 'receptions', 1)

    # --- TARGETS for any real pass (not a sack) ---
    if r['ispass'] and not r['issack'] and r.get('isplay', True):
        tname = target_name(d)
        if tname:
            add(stats, (tname, off), 'targets', 1)
            add(stats_game, (tname, off, gid), 'targets', 1)

    # --- RUSHING yards / TDs ---
    is_rushish = r['isrush'] or r['playtype'] == 'scramble' or is_text_rush(d)
    if is_rushish:
        official = int(r['yards']) if pd.notna(r.get('yards')) else 0

        # Kneel normalization
        if 'KNEEL' in d.upper():
            kneel_text = extract_yards_clause(d)
            kneel_yards = official if kneel_text is None else kneel_text
            rname = rush_carrier_name(d) or last_tag_name_before_touchdown(d)
            if rname:
                add(stats, (rname, off), 'rush_yds', int(kneel_yards))
                add(stats_game, (rname, off, gid), 'rush_yds', int(kneel_yards))

        else:
            segs = rush_segments(d, official, off)
            if segs:
                for rname, y in segs:
                    add(stats, (rname, off), 'rush_yds', y)
                    add(stats_game, (rname, off, gid), 'rush_yds', y)
            else:
                # Fallback to your original attribution
                rname = (
                    rush_td_scorer_name(d)
                    or rush_carrier_name(d)
                    or last_tag_name_before_touchdown(d)
                )
                if rname:
                    add(stats, (rname, off), 'rush_yds', official)
                    add(stats_game, (rname, off, gid), 'rush_yds', official)

            # TD credit for rush plays
            if td_after:
                scorer = rush_td_scorer_name(d) or last_tag_name_before_touchdown(d)
                if scorer:
                    add(stats, (scorer, off), 'rush_td', 1)
                    add(stats_game, (scorer, off, gid), 'rush_td', 1)

    # --- FUMBLES LOST (defense recovery) ---
    if r['isfumble'] and defense_recovered(d, off):
        pre = d.split('FUMBLES', 1)[0]
        pre_clean = re.sub(r'\([^)]*\)', '', pre)
        last_name = None
        for m in re.finditer(TAG_RE_FULL, pre_clean):
            last_name = m.group('name_full')
        if last_name is None:
            for m in re.finditer(TAG_RE_NAME_ONLY, pre_clean):
                last_name = m.group('name_only')
        if last_name:
            add(stats, (last_name, off), 'fumbles', 1)
            add(stats_game, (last_name, off, gid), 'fumbles', 1)

# =========================
# Build STAR SCHEMA
# =========================

# dim_games
dim_games = (
    pbp[["gameid","gamedate"]]
      .dropna()
      .drop_duplicates()
      .rename(columns={"gameid":"game_id","gamedate":"game_date"})
      .sort_values(["game_date","game_id"])
      .reset_index(drop=True)
)
dim_games["season_year"] = 2024
dim_games["iso_week"] = dim_games["game_date"].dt.isocalendar().week.astype(int)

# dim_teams
teams = pd.Series(pd.unique(pd.concat([
    pbp["offenseteam"].str.upper(), pbp["defenseteam"].str.upper()
]))).dropna().sort_values()
dim_teams = pd.DataFrame({"team_code": teams})
dim_teams.insert(0, "team_id", range(1, len(dim_teams)+1))

# dim_players (one row per (player_name, team_code) with totals)
rows = []
for (pname, tcode), agg in stats.items():
    rows.append({
        "player_name": pname,
        "team_code": tcode,
        "pass_yds": agg["pass_yds"],
        "pass_td":  agg["pass_td"],
        "ints":     agg["ints"],
        "rush_yds": agg["rush_yds"],
        "rush_td":  agg["rush_td"],
        "rec_yds":  agg["rec_yds"],
        "rec_td":   agg["rec_td"],
        "fumbles_lost": agg["fumbles"],
        "targets":  agg["targets"],
        "receptions": agg["receptions"],
    })
dim_players = pd.DataFrame(rows)

# ensure numeric cols are numeric (no NaNs)
num_cols = ["pass_yds","pass_td","ints","rush_yds","rush_td","rec_yds","rec_td","fumbles_lost","targets","receptions"]
for c in num_cols:
    if c in dim_players.columns:
        dim_players[c] = pd.to_numeric(dim_players[c], errors="coerce").fillna(0).astype(int)

dim_players.insert(0, "player_id", range(1, len(dim_players)+1))

# Position: QB vs RB vs WR/TE
def infer_pos(row):
    if row.pass_yds >= (row.rush_yds + row.rec_yds):
        return "QB"
    return "RB" if row.rush_yds > row.rec_yds else "WR/TE"

dim_players["position"] = dim_players.apply(infer_pos, axis=1)

# Fantasy points (three variants; rounded)
fp_base = (
    0.04 * dim_players["pass_yds"] + 4 * dim_players["pass_td"] - 2 * dim_players["ints"]
  + 0.1  * dim_players["rush_yds"] + 6 * dim_players["rush_td"]
  + 0.1  * dim_players["rec_yds"]  + 6 * dim_players["rec_td"]
  - 2 * dim_players["fumbles_lost"]
)
dim_players["fp24_nonppr"]  = fp_base.round(2)
dim_players["fp24_halfppr"] = (fp_base + 0.5 * dim_players["receptions"]).round(2)
dim_players["fp24_ppr"]     = (fp_base + 1.0 * dim_players["receptions"]).round(2)
# optional legacy column
dim_players["fp24"] = dim_players["fp24_nonppr"]

# Friendly display
dim_players["player_display"] = dim_players["player_name"] + " (" + dim_players["team_code"].fillna("NA") + ")"

# fact_player_game (grain: player + team + game)
game_map = dim_games.set_index("game_id")[["game_date","iso_week","season_year"]]
defense_mode = (
    pbp.assign(offenseteam=pbp["offenseteam"].str.upper(),
               defenseteam=pbp["defenseteam"].str.upper())
       .groupby(["gameid","offenseteam"])["defenseteam"]
       .agg(lambda s: s.mode().iat[0] if not s.mode().empty else None)
       .reset_index()
       .rename(columns={"gameid":"game_id","offenseteam":"team_code","defenseteam":"opp_code"})
)

fact_rows = []
for (pname, tcode, gid), agg in stats_game.items():
    fp_base = (
        0.04 * agg["pass_yds"] + 4 * agg["pass_td"] - 2 * agg["ints"]
      + 0.1  * agg["rush_yds"] + 6 * agg["rush_td"]
      + 0.1  * agg["rec_yds"]  + 6 * agg["rec_td"]
      - 2 * agg["fumbles"]
    )
    fact_rows.append({
        "game_id": gid,
        "player_name": pname,
        "team_code": tcode,
        "pass_yds": agg["pass_yds"],
        "pass_td":  agg["pass_td"],
        "ints":     agg["ints"],
        "rush_yds": agg["rush_yds"],
        "rush_td":  agg["rush_td"],
        "rec_yds":  agg["rec_yds"],
        "rec_td":   agg["rec_td"],
        "fumbles_lost": agg["fumbles"],
        "targets":  agg["targets"],
        "receptions": agg["receptions"],
        "fantasypoints_nonppr": round(fp_base, 2),
        "fantasypoints_halfppr": round(fp_base + 0.5 * agg["receptions"], 2),
        "fantasypoints_ppr": round(fp_base + 1.0 * agg["receptions"], 2),
        # optional legacy
        "fantasypoints": round(fp_base, 2),
    })
fact_player_game = pd.DataFrame(fact_rows)

# attach dates & weeks
fact_player_game = fact_player_game.merge(
    game_map, left_on="game_id", right_index=True, how="left"
)

# attach team & player surrogate keys
team_id_map = dict(zip(dim_teams["team_code"], dim_teams["team_id"]))
pid_map = dict(zip(
    dim_players.set_index(["player_name","team_code"]).index, dim_players["player_id"]
))
fact_player_game["team_id"] = fact_player_game["team_code"].map(team_id_map)
fact_player_game["player_id"] = fact_player_game.apply(
    lambda r: pid_map.get((r["player_name"], r["team_code"])), axis=1
)

# optional opponent id
fact_player_game = fact_player_game.merge(
    defense_mode, on=["game_id","team_code"], how="left"
)
fact_player_game["opp_team_id"] = fact_player_game["opp_code"].map(team_id_map)

# final column order
fact_player_game = fact_player_game[[
    "game_id","player_id","team_id","opp_team_id",
    "game_date","season_year","iso_week",
    "player_name","team_code",
    "pass_yds","pass_td","ints","rush_yds","rush_td","rec_yds","rec_td",
    "fumbles_lost","targets","receptions",
    "fantasypoints_nonppr","fantasypoints_halfppr","fantasypoints_ppr",
    "fantasypoints"  # legacy non-PPR
]]

# --- Save CSVs for Power BI ---
dim_games.to_csv("dim_games.csv", index=False)
dim_teams.to_csv("dim_teams.csv", index=False)
dim_players.to_csv("dim_players.csv", index=False)
fact_player_game.to_csv("fact_plays.csv", index=False)

print("done:",
      f"players={len(dim_players):,}",
      f"teams={len(dim_teams):,}",
      f"games={len(dim_games):,}",
      f"facts(player-game)={len(fact_player_game):,}")

# --- Optional Postgres ---
from sqlalchemy import create_engine
engine = create_engine('postgresql+psycopg2://leanderlu:Xinxiang12.0@localhost:5432/postgres', future=True)
with engine.begin() as conn:
    dim_teams.to_sql("dim_teams", conn, if_exists="replace", index=False)
    dim_games.to_sql("dim_games", conn, if_exists="replace", index=False)
    dim_players.to_sql("dim_players", conn, if_exists="replace", index=False)
    fact_player_game.to_sql("fact_plays", conn, if_exists="replace", index=False)
