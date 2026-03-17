import pandas as pd

ipl = pd.read_csv('ipl_matches.csv')

class Points_Table:

#points table
    def matches_played(self,data, team):
        return data[(data['team1'] == team) | (data['team2'] == team)].shape[0]

    def matches_won(self,data, team):
        return data[(data['winning_team'] == team)].shape[0]

    def matches_no_result(self,data, team):
        return data[((data['team1'] == team) | (data['team2'] == team)) & (data['winning_team'] == 'NR')].shape[0]

    ipl.loc[56, ipl.columns[5]] = 'Qualifier 1'
    ipl.loc[57, ipl.columns[5]] = 'Qualifier 2'
    ipl.loc[115, ipl.columns[5]] = 'Qualifier 1'
    ipl.loc[116, ipl.columns[5]] = 'Qualifier 2'
    ipl.loc[174, ipl.columns[5]] = 'Qualifier 1'
    ipl.loc[175, ipl.columns[5]] = 'Qualifier 2'
    ipl.loc[176, ipl.columns[5]] = 'Eliminator'
    ipl.loc[248, ipl.columns[5]] = 'Qualifier 1'
    ipl.loc[250, ipl.columns[5]] = 'Qualifier 2'
    ipl.loc[249, ipl.columns[5]] = 'Eliminator'
    ipl.loc[324, ipl.columns[5]] = 'Qualifier 1'
    ipl.loc[326, ipl.columns[5]] = 'Qualifier 2'
    ipl.loc[325, ipl.columns[5]] = 'Eliminator'

    ipl['season'] = ipl['season'].replace('2007/08', '2008')
    ipl['season'] = ipl['season'].replace('2009/10', '2010')
    ipl['season'] = ipl['season'].replace('2020/21', '2021')

    ipl['season'] = ipl['season'].astype('int')

    # find ipl season(2008-2024)
    def season(self):
        return sorted(ipl.season.unique())

    # points table of each season
    def points_table(self,season):
        df = ipl[ipl['season'] == season]
        temp = pd.DataFrame()
        temp['Team Name'] = (ipl[ipl['season'] == season]['team1'].value_counts() + ipl[ipl['season'] == season]['team2'].value_counts()).index.tolist()
        temp['Matches Played'] = temp['Team Name'].apply(lambda x: self.matches_played(df, x))
        temp['Matches Won'] = temp['Team Name'].apply(lambda x: self.matches_won(df, x))
        temp['No Result'] = temp['Team Name'].apply(lambda x: self.matches_no_result(df, x))
        temp['Points'] = temp['Matches Won'] * 2 + temp['No Result']

        temp.sort_values(['Points','Matches Played'], ascending=False, inplace=True)
        temp.set_index('Team Name', inplace=True)

        return temp

    # season position of ipl team
    def seasonPosition(self,season):
        x = self.points_table(season)
        df = ipl[ipl['season'] == season].copy()
        x['Position'] = x['Points'].rank(ascending=False, method='first').astype('int')
        # x['Position'] = x.Points.rank(ascending=False, method= 'first').astype('object')

        df['LossingTeam'] = df[df['winning_team'] == df['team1']]['team2']._append(df[df['winning_team'] == df['team2']]['team1'])
        final = df[df['match_number'] == 'Final']
        winning_team = final['winning_team'].values[0]
        runner_up = final['LossingTeam'].values[0]
        x.at[winning_team, 'Position'] = 'Winners'
        x.at[runner_up, 'Position'] = 'Runners Up'

        if (season == 2008) or (season == 2009):
            a = df[df['match_number'] == 'Qualifier 1']
            b = df[df['match_number'] == 'Qualifier 2']
            third = a['LossingTeam'].values[0]
            fourth = b['LossingTeam'].values[0]
            x.at[third, 'Position'] = 'Third'
            x.at[fourth, 'Position'] = 'Fourth'

        elif (season == 2010):
            c = df[df['match_number'] == 'Qualifier 1']
            d = df[df['match_number'] == 'Qualifier 2']
            third = c['LossingTeam'].values[0]
            fourth = d['LossingTeam'].values[0]
            x.at[third, 'Position'] = 'Third'
            x.at[fourth, 'Position'] = 'Fourth'

        else:
            q = df[df['match_number'] == 'Qualifier 2']
            e = df[df['match_number'] == 'Eliminator']
            third = q['LossingTeam'].values[0]
            fourth = e['LossingTeam'].values[0]
            x.at[third, 'Position'] = 'Third'
            x.at[fourth, 'Position'] = 'Fourth'

        return x