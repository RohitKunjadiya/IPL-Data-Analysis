import ast
import numpy as np
import pandas as pd
from data import IPLDatabase

db = IPLDatabase()

ipl = db.get_seasons_data()
record = db.get_ball_by_ball_data()

db.close()

# record = pd.read_csv('ipl_ball_by_ball_data.csv')
# ipl = pd.read_csv('ipl_matches.csv')

ipl1 = ipl[~ipl['team1players'].isna()]
# ipl = ipl[ipl['WinningTeam'] != 'NR']

data1 = record.merge(ipl1,on='id',how='inner').copy()

def st(x):
    if x == 'Kings XI Punjab':
        return 'Punjab Kings'
    else:
        return x

def st1(x):
    if x == 'Delhi Daredevils':
        return 'Delhi Capitals'
    else:
        return x

def st2(x):
    if x == 'Rising Pune Supergiant':
        return 'Rising Pune Supergiants'
    else:
        return x


def st3(t):
    if t == 'Royal Challengers Bangalore':
        return 'Royal Challengers Bengaluru'
    else:
        return t


data1['batting_team'] = data1['batting_team'].apply(st)
data1['bowling_team'] = data1['bowling_team'].apply(st)

data1['batting_team'] = data1['batting_team'].apply(st1)
data1['bowling_team'] = data1['bowling_team'].apply(st1)

data1['batting_team'] = data1['batting_team'].apply(st2)
data1['bowling_team'] = data1['bowling_team'].apply(st2)

data1['batting_team'] = data1['batting_team'].apply(st3)
data1['bowling_team'] = data1['bowling_team'].apply(st3)

class Batters:

    # All batters in ipl till 2024
    def batter(self):
        return data1['batter'].unique()

    # strike of player
    def strike_rate(self,player):
        df = data1[data1['batter'] == player]
        runs = df['batsman_run'].sum()
        balls = df['batsman_run'].count()
        wides = data1[data1['extra_type'] == 'wides']
        wcount = wides[wides['batter'] == player]['extras_run'].count()
        sr = runs / (balls - wcount) * 100

        return np.round(sr, 2)

    # batter statistics in ipl of batter till 2024
    def batter_stats(self, batter):
        out = data1[data1['player_out'] == batter].shape[0]

        def parse_players(x):
            try:
                if pd.isna(x):
                    return []

                parsed = ast.literal_eval(x)

                if isinstance(parsed, dict):
                    return list(parsed.values())
                elif isinstance(parsed, list):
                    return parsed
                else:
                    return []
            except Exception as e:
                print("Error:", x, "->", e)
                return []

        t1players = ipl1['team1players'].apply(parse_players)
        t2players = ipl1['team2players'].apply(parse_players)

        team1_match = t1players.apply(lambda players: batter in players)
        team2_match = t2players.apply(lambda players: batter in players)

        Matches_played = (team1_match | team2_match).sum()

        inn = data1[data1['batter'] == batter]['id'].nunique()
        # data[data['batter']=='V Kohli']['id'].drop_duplicates().count()
        # data[data['batter']=='V Kohli']['id'].unique().shape[0]
        not_out = inn - out
        total_run = data1[data1['batter'] == batter]['batsman_run'].sum()

        x = data1[data1['batter'] == batter]

        runs = x.groupby(['batter', 'id'])['batsman_run'].sum()
        fifties = runs[(runs >= 50) & (runs < 100)].shape[0]
        hundreds = runs[runs >= 100].shape[0]
        highest_score = runs.max()

        mask = x[(x['batsman_run'] == 4) & (x['extras_run'] == 0)]
        four = mask.groupby('batter')['batsman_run'].count()

        mask = x[(x['batsman_run'] == 6) & (x['extras_run'] == 0)]
        six = mask.groupby('batter')['batsman_run'].count()

        sr = self.strike_rate(batter)

        avg = round(total_run/out,2)

        d = {
            'Matches': Matches_played,
            'Innings': inn,
            # 'Out': out,
            'NO': not_out,
            'Runs': total_run,
            'HS':highest_score,
            'Average': avg,
            'SR': sr,
            '100s': hundreds,
            '50s': fifties,
            'Fours': four,
            'Six': six}
        return d

    # batter's run against team
    def runs_against_team(self,player):
        bats = data1[data1['batter'] == player]
        tr = bats.groupby('bowling_team')['batsman_run'].sum()
        run = tr.sort_values(ascending=False)

        return pd.DataFrame(run)

    # def runs_against_teamChart(self,player):
    #     bats = data1[data1['batter'] == player]
    #     tr = bats.groupby('bowling_team')['batsman_run'].sum()
    #     run = tr.sort_values(ascending=False)
    #
    #     runs = pd.DataFrame(run).reset_index()
    #     runs.rename(columns={'bowling_team':'Bowling Team','batsman_run':'Runs'},inplace=True)
    #
    #     return runs

    # batter's runs in each season
    def batter_score_seasonwise(self, batter):
        try:
            x = data1[data1['batter'] == batter]

            if x.empty:
                return pd.DataFrame(columns=['Season', 'Runs'])

            y = (
                x.groupby('season')['batsman_run']
                .sum()
                .reset_index()
                .sort_values(by='season')
            )

            y.rename(columns={'season': 'Season', 'batsman_run': 'Runs'}, inplace=True)

            return y[['Season', 'Runs']]

        except Exception as e:
            print("Error in batter_score_seasonwise:", e)
            return pd.DataFrame(columns=['Season', 'Runs'])
    # def batter_score_seasonwise(self, batter):
    #     try:
    #         x = data1[data1['batter'] == batter]
    #         y = x.groupby(['Season', 'batter'])['batsman_run'].sum().sort_values(
    #             ascending=False).reset_index().sort_values(by='Season')
    #         y.rename(columns={'batsman_run': 'Runs'}, inplace=True)

    #         return y[['Season', 'Runs']]
    #     except:
    #         return 'Not Played'

    # top-10 batter's till 2024
    def top_10(self):
        return data1.groupby('batter')['batsman_run'].sum().sort_values(ascending=False).head(10)

    # Highest Strike Rate
    def sr(self):
        df = data1[data1['overs'] > 15]
        x = df.groupby('batter')['batsman_run'].count()
        y = x > 200
        batsman_list = x[y].index.tolist()

        final = df[df['batter'].isin(batsman_list)]
        runs = final.groupby('batter')['batsman_run'].sum()
        balls = final.groupby('batter')['batsman_run'].count()
        sr = (runs / balls) * 100
        srate = np.round(sr, 2).sort_values(ascending=False).head(10)
        sr = pd.DataFrame(srate)
        return sr

    # orange cap holder
    def orange_cap_holder(self):
        data1['ball_played'] = data1['extra_type'].apply(lambda x:0 if x in ['wides'] else 1)
        data1['out'] = (data1['batter'] == data1['player_out']) & (~data1['kind'].isin(['run out', 'retired hurt', 'retired hurt']))
        x = data1.groupby(['season', 'batter'])
        x = x.agg({'batsman_run': 'sum', 'ball_played': 'sum', 'out': 'sum'}).rename(columns={'batsman_run': 'Runs', 'ball_played': 'Balls'}).sort_values(by='Runs',ascending=False).reset_index().drop_duplicates('season', keep='first').sort_values(by='season')
        x['Strike Rate'] = round(x['Runs'] / x['Balls'] * 100, 2)
        x['Average'] = round(x['Runs'] / x['out'], 2)
        x.set_index('season', inplace=True)
        return x