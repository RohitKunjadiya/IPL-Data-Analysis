import pandas as pd
from data import IPLDatabase

db = IPLDatabase()

ipl = db.get_seasons_data()

db.close()
# ipl = pd.read_csv('ipl_matches.csv')

ipl.sort_values(['date'],inplace=True)

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


ipl['team1'] = ipl['team1'].apply(st)
ipl['team2'] = ipl['team2'].apply(st)
ipl['winning_team'] = ipl['winning_team'].apply(st)

ipl['team1'] = ipl['team1'].apply(st1)
ipl['team2'] = ipl['team2'].apply(st1)
ipl['winning_team'] = ipl['winning_team'].apply(st1)

ipl['team1'] = ipl['team1'].apply(st2)
ipl['team2'] = ipl['team2'].apply(st2)
ipl['winning_team'] = ipl['winning_team'].apply(st2)

ipl['team1'] = ipl['team1'].apply(st3)
ipl['team2'] = ipl['team2'].apply(st3)
ipl['winning_team'] = ipl['winning_team'].apply(st3)


class IPL:

    def teams(self):
        return list(ipl['team1'].unique())
        # print(teams())

    def playing_teams(self):
        return list(ipl[ipl['season'] == '2025']['team1'].unique())
    
    def cities(self):
        return list(ipl[ipl['season'] == '2025']['city'].unique())

    # teamVsteam
    def teamVsteam(self,team_1, team_2):

        teams = ipl['team1'].unique()
        if team_1 in teams and team_2 in teams:
            df = ipl[
                (ipl['team1'] == team_1) & (ipl['team2'] == team_2) | (ipl['team1'] == team_2) & (ipl['team2'] == team_1)]
            tm = df.shape[0]

            t1_won = df[df['winning_team'] == team_1].shape[0]
            t2_won = df[df['winning_team'] == team_2].shape[0]

            #     t1_loss = df[df['winning_team'] != team1].shape[0]
            #     t2_loss = df[df['winning_team'] != team2].shape[0]

            nr = tm - (t1_won + t2_won)

            response = {
                'Total Matches': str(tm),
                team_1: str(t1_won),
                team_2: str(t2_won),
                'No Result': str(nr),
            }

            return response
        else:
            return {'message': 'Invalid Team Name'}

    # team record
    def team_record(self,team):
        teams = list(ipl['team1'].unique())

        if team in teams:
            mask = ipl[(ipl['team1'] == team) | (ipl['team2'] == team)]
            tm = mask.shape[0]
            title = ipl[(ipl['match_number'] == 'Final') & (ipl['winning_team'] == team)].shape[0]
            won = mask[mask['winning_team'] == team].shape[0]
            loss = mask[mask['winning_team'] != team].shape[0] - mask[mask['winning_team'] == 'NR'].shape[0]
            nr = mask[mask['winning_team'] == 'NR'].shape[0]

            response = {
                'Team': str(team),
                'Total Matches': str(tm),
                'Won': str(won),
                'Loss': str(loss),
                'No Result': str(nr),
                'Title': str(title)
            }
            return response
        else:
            return {'message': 'Invalid team name'}

    # pie chart
    def team_recordPie(self,team):
        teams = list(ipl['team1'].unique())

        if team in teams:
            mask = ipl[(ipl['team1'] == team) | (ipl['team2'] == team)]
            tm = mask.shape[0]
            title = ipl[(ipl['match_number'] == 'Final') & (ipl['winning_team'] == team)].shape[0]
            won = mask[mask['winning_team'] == team].shape[0]
            loss = mask[mask['winning_team'] != team].shape[0] - mask[mask['winning_team'] == 'NR'].shape[0]
            nr = mask[mask['winning_team'] == 'NR'].shape[0]

            response = {

                'Won': str(won),
                'Loss': str(loss),
                'No Result': str(nr),
            }

            response = pd.DataFrame(pd.DataFrame(response, index=[1]).stack()).reset_index()
            response.drop('level_0', axis=1, inplace=True)
            response.rename(columns={'level_1': 'Team Name', 0: 'Results'}, inplace=True)

            return response
        else:
            return {'message': 'Invalid team name'}

    # pie chart of h2h(2 teams)
    def teamVsteamPie(self,team_1, team_2):

        teams = list(ipl['team1'].unique())
        if team_1 in teams and team_2 in teams:
            df = ipl[(ipl['team1'] == team_1) & (ipl['team2'] == team_2) | (ipl['team1'] == team_2) & (ipl['team2'] == team_1)]
            tm = df.shape[0]

            t1_won = df[df['winning_team'] == team_1].shape[0]
            t2_won = df[df['winning_team'] == team_2].shape[0]

            #     t1_loss = df[df['winning_team'] != team_1].shape[0]
            #     t2_loss = df[df['winning_team'] != team_2].shape[0]

            nr = tm - (t1_won + t2_won)

            response = {
                team_1: str(t1_won),
                team_2: str(t2_won),
                'No Result': str(nr),
            }
            response = pd.DataFrame(pd.DataFrame(response, index=[1]).stack()).reset_index()
            response.drop('level_0', axis=1, inplace=True)
            response.rename(columns={'level_1': 'Team Name', 0: 'Results'}, inplace=True)

            return response
        else:
            return {'message': 'Invalid Team Name'}