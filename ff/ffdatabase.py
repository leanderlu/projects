import pandas as pd
import re
from collections import defaultdict, Counter
from sqlalchemy import create_engine, text
from datetime import datetime

# Load and concatenate PBP data
df_2023 = pd.read_csv('pbp_2023.csv')
df_2024 = pd.read_csv('pbp_2024.csv')
pbp = pd.concat([df_2023, df_2024], ignore_index=True)

# Helper Functions
def extract_players(desc):
    return re.findall(r'\b[A-Z]\.[A-Z][A-Z]+\b', str(desc))

def get_position(player):
    return 'QB' if pass_attempt_counts.get(player, 0) >= rush_attempt_counts.get(player, 0) else 'RB/WR/TE'

def calc_fantasy_for_play(row):
    players = extract_players(row['Description'])
    if not players:
        return []

    results = []
    if row['IsPass']:
        qb = players[0]
        qb_points = row['Yards'] / 25
        if row['IsTouchdown']: qb_points += 4
        if row['IsInterception']: qb_points -= 2
        results.append((qb, qb_points))

        if len(players) > 1:
            receiver = players[1]
            rec_points = row['Yards'] / 10
            if row['IsTouchdown']: rec_points += 6
            results.append((receiver, rec_points))

    elif row['IsRush']:
        rusher = players[0]
        rush_points = row['Yards'] / 10
        if row['IsTouchdown']: rush_points += 6
        results.append((rusher, rush_points))

    if row['IsFumble']:
        results = [(p, pts - 2) for p, pts in results]

    return results

def lowercase_columns(df):
    df.columns = df.columns.str.lower()
    return df

# Count pass and rush attempts
pass_attempt_counts = Counter()
rush_attempt_counts = Counter()

for _, row in pbp.iterrows():
    players = extract_players(row['Description'])
    if not players:
        continue
    if row['IsPass']:
        pass_attempt_counts[players[0]] += 1
    elif row['IsRush']:
        rush_attempt_counts[players[0]] += 1

# Calculate player fantasy points per season
player_fp = defaultdict(lambda: {'2023': 0, '2024': 0})
player_last_team = {}

for _, row in pbp.iterrows():
    year = str(row['SeasonYear'])
    team = row['OffenseTeam']
    for player, pts in calc_fantasy_for_play(row):
        player_fp[player][year] += pts
        player_last_team[player] = team

all_players = set(pass_attempt_counts) | set(rush_attempt_counts)
final_positions = {p: get_position(p) for p in all_players}

summary_data = []
for player, pts in player_fp.items():
    summary_data.append({
        'player_name': player,
        'fp23': pts.get('2023', 0),
        'fp24': pts.get('2024', 0),
        'position': final_positions.get(player, 'RB/WR/TE'),
        'team': player_last_team.get(player)
    })

summary_df = pd.DataFrame(summary_data)

# Add fantasy points per play
pbp['FantasyPoints'] = pbp.apply(lambda row: round(sum(pts for _, pts in calc_fantasy_for_play(row)), 1), axis=1)
pbp['GameDate'] = pd.to_datetime(pbp['GameDate'])
pbp['Week'] = pbp['GameDate'].dt.isocalendar().week
pbp['SeasonYear'] = pbp['SeasonYear'].astype(str)
pbp['player_name'] = pbp.apply(lambda row: extract_players(row['Description'])[0] if extract_players(row['Description']) else None, axis=1)

# Weekly totals
weekly_totals = (
    pbp.groupby(['SeasonYear', 'Week', 'player_name'])['FantasyPoints']
    .sum()
    .round(1)
    .reset_index()
    .rename(columns={'FantasyPoints': 'WeeklyFantasyPoints'})
)
pbp = pbp.merge(weekly_totals, on=['SeasonYear', 'Week', 'player_name'], how='left')

# PostgreSQL connection
engine = create_engine('postgresql+psycopg2://leanderlu:Xinxiang12.0@localhost:5432/postgres', future=True)

with engine.begin() as conn:
    # dim_teams
    teams_offense = pbp['OffenseTeam'].dropna().unique()
    df_teams = pd.DataFrame({'team_code': sorted(teams_offense)}).reset_index()
    df_teams.rename(columns={'index': 'team_id'}, inplace=True)
    df_teams = lowercase_columns(df_teams)
    df_teams.to_sql('dim_teams', conn, if_exists='replace', index=False)

    # dim_games: new version with team_1_code and team_2_code
    team_games = pbp[['GameId', 'GameDate', 'SeasonYear', 'OffenseTeam', 'DefenseTeam']].drop_duplicates()

    def get_teams(group):
        teams = set(group['OffenseTeam']).union(set(group['DefenseTeam']))
        teams = sorted(teams)
        if len(teams) == 1:
            teams.append(None)
        return pd.Series(teams[:2], index=['team_1_code', 'team_2_code'])

    df_games = (
        team_games.groupby(['GameId', 'GameDate', 'SeasonYear'])
        .apply(get_teams)
        .reset_index()
        .rename(columns={
            'GameId': 'game_id',
            'GameDate': 'game_date',
            'SeasonYear': 'season_year'
        })
    )
    df_games = lowercase_columns(df_games)
    df_games.to_sql('dim_games', conn, if_exists='replace', index=False)


    # dim_players
    summary_df = lowercase_columns(summary_df)
    summary_df['fp23'] = summary_df['fp23'].round(1)
    summary_df['fp24'] = summary_df['fp24'].round(1)
    summary_df.to_sql('dim_players', conn, if_exists='replace', index=False)

    # Join team_id to pbp
    dim_teams_df = pd.read_sql(text('SELECT team_id, team_code FROM dim_teams'), conn)
    pbp = pbp.merge(dim_teams_df.rename(columns={'team_id': 'offense_team_id', 'team_code': 'OffenseTeam'}),
                    on='OffenseTeam', how='left')

    # fact_plays — player-week level
    fact_plays_df = (
        pbp.groupby(['player_name', 'SeasonYear', 'Week'])
        .agg({
            'WeeklyFantasyPoints': 'first',
            'offense_team_id': lambda x: x.mode().iloc[0] if not x.mode().empty else None,
            'GameId': 'first'
        })
        .reset_index()
        .rename(columns={
            'SeasonYear': 'season_year',
            'WeeklyFantasyPoints': 'fantasy_points',
            'GameId': 'game_id'
        })
    )
    fact_plays_df = lowercase_columns(fact_plays_df)
    fact_plays_df.to_sql('fact_plays', conn, if_exists='replace', index=False)

# Export for Tableau or debugging
pbp.to_csv('pbp.csv', index=False)
fact_plays_df.to_csv('fact_plays.csv', index=False)
summary_df.to_csv('dim_players.csv', index=False)
df_teams.to_csv('dim_teams.csv', index=False)
df_games.to_csv('dim_games.csv', index=False)


# with engine.connect() as conn: #    
#   print(pd.read_sql(text("SELECT * FROM fact_plays LIMIT 5"), conn)) #     
#   print(pd.read_sql(text("SELECT * FROM dim_games LIMIT 5"), conn)) #     
#   print(pd.read_sql(text("SELECT * FROM dim_teams LIMIT 5"), conn)) #     
#   print(pd.read_sql(text("SELECT * FROM dim_players LIMIT 5"), conn))