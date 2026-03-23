import pandas as pd
from data import IPLDatabase

db = IPLDatabase()

ipl = db.get_seasons_data()
record = db.get_ball_by_ball_data()

db.close()

# record = pd.read_csv('ipl_ball_by_ball_data.csv')
# ipl = pd.read_csv('ipl_matches.csv')

ipl = ipl[~ipl['team1players'].isna()]

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

data = record.merge(ipl,on='id',how='inner').copy()

data['batting_team'] = data['batting_team'].apply(st)
data['bowling_team'] = data['bowling_team'].apply(st)

data['batting_team'] = data['batting_team'].apply(st1)
data['bowling_team'] = data['bowling_team'].apply(st1)

data['batting_team'] = data['batting_team'].apply(st2)
data['bowling_team'] = data['bowling_team'].apply(st2)

data['batting_team'] = data['batting_team'].apply(st3)
data['bowling_team'] = data['bowling_team'].apply(st3)

class Bowlers:

    # All batters in ipl till 2024
    def batter(self):
        return data['batter'].unique()

    # All bowlers in ipl till 2024
    def bowler(self):
        return data['bowler'].unique()

    # batter vs bowler h2h
    def batterVsbowler(self,batter, bowler):
        data['ball_played'] = data['extra_type'].apply(lambda x: 0 if x in ['wides'] else 1)
        data['out'] = (data['batter'] == data['player_out']) & (~data['kind'].isin(['run out', 'retired hurt', 'retired hurt']))
        batter_df = data[data['batter'] == batter]
        bowler_df = batter_df[batter_df['bowler'] == bowler]

        if batter == bowler:
            return 'Not Possible!'
        else:
            x = pd.DataFrame(bowler_df.agg({'batsman_run': 'sum', 'ball_played': 'sum', 'out': 'sum'})).T.rename(
                columns={'batsman_run': 'Runs', 'ball_played': 'Balls', 'out': 'Out'})
            x['batter'] = batter
            x['bowler'] = bowler
            x['Fours'] = bowler_df[bowler_df['batsman_run'] == 4].shape[0]
            x['Sixes'] = bowler_df[bowler_df['batsman_run'] == 6].shape[0]
            x['Strike Rate'] = round(x['Runs'] / x['Balls'] * 100, 2)
            if x['Strike Rate'].isna().any():
                x['Strike Rate'].fillna(0, inplace=True)
            x['Average'] = round(x['Runs'] / x['Out'], 2)
            x.loc[x['Out'] == 0, 'Average'] = 0
            x = x.iloc[:, [3, 4, 0, 1, 5, 6, 2, 7, 8]]
            x.set_index('batter', inplace=True)
            return x

    # bowler wickets in ipl till 2024
    def bowler_wickets(self, bowler):
        l = ['caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'retired hurt',
             'hit wicket']
        x = data[data['kind'].isin(l)]
        df = x[x['bowler'] == bowler]
        if df.empty:
            return 0
        else:
            return df.groupby('bowler')['is_wicket_delivery'].sum().values[0]

    # best figure of any bowler
    def best_figure(self, bowler):
        wct = data[data['bowler'] == bowler]
        wct['bowlers_run'] = wct['extra_type'].apply(lambda x: 0 if x in ['legbyes', 'byes'] else 1) * wct['total_run']
        wct['out'] = (wct['batter'] == wct['player_out']) & (~wct['kind'].isin(['run out', 'retired hurt', 'retired hurt']))
        wc = wct.groupby(['id', 'batting_team'])[['bowlers_run', 'out']].sum().reset_index().sort_values(['out','bowlers_run'],ascending=[False,True]).head(1)
        return wc[['batting_team', 'bowlers_run', 'out']].set_index('batting_team').rename(columns={'bowlers_run': 'Runs', 'out': 'Wickets'})

    # bar-chart of bowlers wicket against each team
    def wicket_against_teamChart(self, player):
        l = ['caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'retired hurt',
             'hit wicket', 'obstructing the field', 'retired out']

        x = data[data['kind'].isin(l)]
        wct = x[x['bowler'] == player]
        wc = wct.groupby('batting_team')['is_wicket_delivery'].sum()
        return wc.reset_index().rename(columns={'is_wicket_delivery': 'Wickets'})

    # def wicket_against_team(self, player):
    #     l = ['caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'retired hurt',
    #          'hit wicket', 'obstructing the field', 'retired out']
    #     x = data[data['kind'].isin(l)]
    #     wct = x[x['bowler'] == player]
    #     wc = wct.groupby('batting_team')['is_wicket_delivery'].sum()
    #     return wc.reset_index().rename(columns={'is_wicket_delivery': 'Wickets'}).set_index('batting_team')

    # bar-chart of bowlers wicket each season
    def wickets_seasonwiseChart(self, bowler):
        x = data[data['bowler'] == bowler]
        l = ['caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'retired hurt',
             'hit wicket', 'obstructing the field', 'retired out']
        y = x[x['kind'].isin(l)]
        z = y.groupby(['season', 'bowler'])['is_wicket_delivery'].sum().sort_values(
            ascending=False).reset_index().sort_values(by='season')
        a = z[['season', 'is_wicket_delivery']]
        return a.rename(columns={'is_wicket_delivery': 'Wickets'})

    # def wickets_seasonwise(self, bowler):
    #     x = data[data['bowler'] == bowler]
    #     l = ['caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'retired hurt',
    #          'hit wicket', 'obstructing the field', 'retired out']
    #     y = x[x['kind'].isin(l)]
    #     z = y.groupby(['season', 'bowler'])['is_wicket_delivery'].sum().sort_values(
    #         ascending=False).reset_index().sort_values(by='season')
    #     a = z[['season', 'is_wicket_delivery']]
    #     return a.rename(columns={'is_wicket_delivery': 'Wickets'}).set_index('season')

    # top-10 wicket-takers in ipl till 2024
    def wickets(self):
        l = ['caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'retired hurt',
             'hit wicket', 'obstructing the field', 'retired out']
        x = data[data['kind'].isin(l)]
        wickets = x.groupby('bowler')['kind'].count().sort_values(ascending=False)
        return wickets.head(10)

    # top-10 battles(batter-vs-bowler)
    def h2h_bowler(self):
        data['out'] = (data['batter'] == data['player_out']) & (~data['kind'].isin(['run out', 'retired hurt', 'retired hurt']))
        return data.groupby(['batter', 'bowler']).agg({
            'batsman_run': 'sum',
            'out': 'sum'
        }).sort_values(by=["out", "batsman_run"], ascending=[False, True]).reset_index().set_index('batter').head(10)

    # purple cap holder
    def purple_cap(self):
        data['is_wicket_delivery'] = data['kind'].apply(
            lambda x: 1 if x in ['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket'] else 0)
        data['bowlers_run'] = data['extra_type'].apply(lambda x: 0 if x in ['legbyes', 'byes'] else 1) * data['total_run']
        data['islegelball'] = data['extra_type'].apply(lambda x: 0 if x in ['wides', 'noballs'] else 1)

        y = data.groupby(['season', 'bowler'], as_index=False)[['is_wicket_delivery', 'bowlers_run', 'islegelball']].sum()
        y['economy'] = round(y['bowlers_run'] / y['islegelball'] * 6,2)
        purple_caps = y.sort_values(by=['is_wicket_delivery', 'economy'], ascending=[False, True]).drop_duplicates(
            'season', keep='first').sort_values('season')
        purple_caps = purple_caps.reset_index()
        purple_caps.drop('index', axis=1, inplace=True)
        purple_caps.set_index('season', inplace=True)

        return purple_caps