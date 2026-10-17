"""Validate only data/processed/matches.csv (never reads RAW files)."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'data' / 'processed' / 'matches.csv'
REPORT_DIR = ROOT / 'documentation' / 'data_validation'
SUMMARY = REPORT_DIR / 'matches_validation_summary.csv'
ISSUES = REPORT_DIR / 'matches_validation_issues.csv'

CORE = ['MatchID','Season','Date','HomeTeam','AwayTeam','FTHG','FTAG','FTR']
HALF = ['HTHG','HTAG','HTR']
STATS = ['Referee','HS','AS','HST','AST','HF','AF','HC','AC','HY','AY','HR','AR']
EXPECTED_SEASONS = [f'{year}/{(year+1)%100:02d}' for year in range(1992,2026)]

def main():
    if not INPUT.is_file():
        raise FileNotFoundError(f'Missing processed file: {INPUT}')
    df = pd.read_csv(INPUT, dtype={'Season':'string','HomeTeam':'string','AwayTeam':'string','FTR':'string','HTR':'string'}, low_memory=False)
    missing = sorted(set(CORE + HALF + STATS) - set(df.columns))
    if missing:
        raise ValueError(f'Missing columns: {missing}')
    issues = []
    def flag(mask, kind, detail):
        count = int(mask.sum())
        if count:
            for i in df.index[mask]:
                row = df.loc[i]
                issues.append({'row_in_csv':int(i)+2,'MatchID':row['MatchID'],'Season':row['Season'],'Date':row['Date'],'HomeTeam':row['HomeTeam'],'AwayTeam':row['AwayTeam'],'issue':kind,'detail':detail})
        return count
    dates = pd.to_datetime(df['Date'],format='%Y-%m-%d',errors='coerce')
    flag(dates.isna(),'INVALID_DATE','Date must be YYYY-MM-DD')
    season_year = pd.to_numeric(df['Season'].str.extract(r'^(\d{4})/\d{2}$',expand=False),errors='coerce')
    expected_label = season_year.map(lambda y: f'{int(y)}/{(int(y)+1)%100:02d}' if pd.notna(y) else '')
    flag(season_year.isna() | df['Season'].ne(expected_label).fillna(True),'INVALID_SEASON','Expected YYYY/YY')
    flag(df[CORE].isna().any(axis=1),'MISSING_CORE','Core match field missing')
    flag(df['HomeTeam'].fillna('').str.strip().eq('') | df['AwayTeam'].fillna('').str.strip().eq(''),'EMPTY_TEAM','Team name empty')
    flag(df['HomeTeam'].eq(df['AwayTeam']).fillna(False),'SAME_TEAM','Home and away team identical')
    ids = pd.to_numeric(df['MatchID'],errors='coerce')
    flag(ids.isna() | (ids%1!=0) | ids.duplicated(keep=False),'INVALID_MATCH_ID','MatchID must be a unique integer')
    flag(df.duplicated(['Season','HomeTeam','AwayTeam'],keep=False),'DUPLICATE_FIXTURE','Same home-away pairing in season')
    hg = pd.to_numeric(df['FTHG'],errors='coerce'); ag = pd.to_numeric(df['FTAG'],errors='coerce')
    bad_goals = hg.isna() | ag.isna() | (hg<0) | (ag<0) | (hg%1!=0) | (ag%1!=0)
    flag(bad_goals,'INVALID_GOALS','Full-time goals must be nonnegative integers')
    expected_ftr = pd.Series(np.select([hg>ag,hg<ag],['H','A'],default='D'),index=df.index)
    flag(~bad_goals & df['FTR'].ne(expected_ftr).fillna(True),'RESULT_MISMATCH','FTR disagrees with full-time goals')
    flag(~df['FTR'].isin(['H','D','A']),'INVALID_FTR','FTR must be H, D or A')
    valid_season = season_year.notna()
    out_of_year = valid_season & dates.notna() & ~((dates.dt.year==season_year) | (dates.dt.year==season_year+1))
    flag(out_of_year,'OUT_OF_SEASON_DATE','Date year outside season span')
    half_applicable = season_year.ge(1995).fillna(False)
    stats_applicable = season_year.ge(2000).fillna(False)
    flag(df.loc[:,HALF].notna().any(axis=1) & ~half_applicable,'UNEXPECTED_HALF_DATA','Half-time values before 1995/96')
    flag(df.loc[:,STATS].notna().any(axis=1) & ~stats_applicable,'UNEXPECTED_STATS','Statistics before 2000/01')
    flag(df[HALF].isna().any(axis=1) & half_applicable,'MISSING_HALF_DATA','Half-time data expected from 1995/96')
    flag(df[STATS].isna().any(axis=1) & stats_applicable,'MISSING_STATS','Statistics expected from 2000/01')
    hthg = pd.to_numeric(df['HTHG'],errors='coerce'); htag = pd.to_numeric(df['HTAG'],errors='coerce')
    bad_half = half_applicable & (hthg.isna()|htag.isna()|(hthg<0)|(htag<0)|(hthg%1!=0)|(htag%1!=0))
    flag(bad_half,'INVALID_HALF_GOALS','Half-time goals must be nonnegative integers')
    expected_htr = pd.Series(np.select([hthg>htag,hthg<htag],['H','A'],default='D'),index=df.index)
    flag(half_applicable & ~bad_half & df['HTR'].ne(expected_htr).fillna(True),'HALF_RESULT_MISMATCH','HTR disagrees with half-time goals')
    flag(half_applicable & ~bad_half & ((hthg>hg)|(htag>ag)),'HALF_GOALS_EXCEED_FULL','Half-time goals exceed full-time goals')
    for col in STATS:
        if col == 'Referee': continue
        v = pd.to_numeric(df[col],errors='coerce')
        flag(stats_applicable & (v.isna() | (v<0) | (v%1!=0)),f'INVALID_{col}','Stat must be nonnegative integer')
    flag(stats_applicable & (pd.to_numeric(df['HST'],errors='coerce')>pd.to_numeric(df['HS'],errors='coerce')),'HOME_SHOTS_MISMATCH','Shots on target exceed shots')
    flag(stats_applicable & (pd.to_numeric(df['AST'],errors='coerce')>pd.to_numeric(df['AS'],errors='coerce')),'AWAY_SHOTS_MISMATCH','Shots on target exceed shots')
    rows=[]
    for season in EXPECTED_SEASONS:
        d=df[df.Season.eq(season).fillna(False)]
        year=int(season[:4]); expected_teams=22 if year<=1994 else 20
        expected_matches=expected_teams*(expected_teams-1)
        teams=set(d.HomeTeam.dropna()) | set(d.AwayTeam.dropna())
        counts=pd.concat([d.HomeTeam.value_counts().rename('home'),d.AwayTeam.value_counts().rename('away')],axis=1).fillna(0)
        bad_team_counts=int(((counts.home!=expected_teams-1)|(counts.away!=expected_teams-1)).sum())
        status='PASS' if len(d)==expected_matches and len(teams)==expected_teams and bad_team_counts==0 else 'FAIL'
        if status=='FAIL':
            issues.append({'row_in_csv':None,'MatchID':None,'Season':season,'Date':None,'HomeTeam':None,'AwayTeam':None,'issue':'SEASON_STRUCTURE','detail':f'matches={len(d)}/{expected_matches}; teams={len(teams)}/{expected_teams}; incorrect team home/away counts={bad_team_counts}'})
        rows.append({'Season':season,'Matches':len(d),'ExpectedMatches':expected_matches,'Teams':len(teams),'ExpectedTeams':expected_teams,'TeamsWithIncorrectHomeAwayCount':bad_team_counts,'FirstDate':d.Date.min() if len(d) else None,'LastDate':d.Date.max() if len(d) else None,'Status':status})
    extra_seasons=set(df.Season.dropna())-set(EXPECTED_SEASONS)
    for season in sorted(extra_seasons):
        issues.append({'row_in_csv':None,'MatchID':None,'Season':season,'Date':None,'HomeTeam':None,'AwayTeam':None,'issue':'UNEXPECTED_SEASON','detail':'Not in expected 1992/93–2025/26 range'})
    if len(df)!=13166:
        issues.append({'row_in_csv':None,'MatchID':None,'Season':None,'Date':None,'HomeTeam':None,'AwayTeam':None,'issue':'TOTAL_MATCH_COUNT','detail':f'Expected 13166, got {len(df)}'})
    REPORT_DIR.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(SUMMARY,index=False,encoding='utf-8-sig')
    pd.DataFrame(issues,columns=['row_in_csv','MatchID','Season','Date','HomeTeam','AwayTeam','issue','detail']).to_csv(ISSUES,index=False,encoding='utf-8-sig')
    print(f'Input: {INPUT}\nRows: {len(df)} | Seasons: {df.Season.nunique()} | Issues: {len(issues)}')
    print(pd.DataFrame(rows).to_string(index=False))
    print(f'\nSummary: {SUMMARY}\nIssues: {ISSUES}')
    print('\nVALIDATION ' + ('PASS' if not issues else 'FAIL'))
    if issues:
        print(pd.DataFrame(issues)['issue'].value_counts().to_string())
        raise SystemExit(1)

if __name__=='__main__':
    main()
