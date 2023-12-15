# type: ignore
# flake8: noqa
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#| label: load-data
import pandas as pd
import numpy as np
combined_df = pd.read_csv("assets/nfl_combined.csv")
combined_df.head()
#
#
#
#
#
# Get the range of seasons from the df
first_year_full = combined_df['season'].min()
last_year_full = combined_df['season'].max()
print(first_year_full, last_year_full)
year_range_full = list(range(first_year_full, last_year_full + 1))
class Season:
    def __init__(self, year, team_id_list):
        self.year = year
        # Keys will be {year}_{team}
        self.teams = {team_id: SeasonTeam(team_id, self.year) for team_id in team_id_list}
        
    def __str__(self):
        all_teams = self.get_team_list()
        first_team = all_teams[0]
        last_team = all_teams[-1]
        return f"Season[year={self.get_year()},{self.get_num_teams()} teams: [{first_team}, ..., {last_team}]]"
    
    def __repr__(self):
        return self.__str__()
        
    def add_team(self, team_id):
        self.teams[team_id] = SeasonTeam(team_id, self.year)
        
    def get_num_teams(self):
        return len(self.get_team_list())
    
    def get_team(self, team_id):
        return self.teams[team_id]
    
    def get_team_list(self):
        return list(self.teams.keys())
    
    def get_team_record(self, team_id):
        return self.get_team(team_id).get_record()
    
    def get_year(self):
        return self.year
    
    def record_result(self, team_id, result):
        self.get_team(team_id).record_result(result)

class SeasonTeam:
    def __init__(self, team, year):
        self.team = team
        self.year = year
        # (w,l,t), first week starts at (0,0,0)
        self.record = np.array([0,0,0])
    
    def get_record(self):
        return self.record
    
    def record_result(self, result):
        new_record = self.get_record() + result
        self.set_record(new_record)
        
    def set_record(self, new_record):
        self.record = new_record
#
#
#
#
#
#| label: season-dict
unique_home = set(combined_df['away_team'].unique())
unique_away = set(combined_df['home_team'].unique())
unique_teams_set = unique_home.union(unique_away)
team_ids = sorted(list(unique_teams_set))
print(team_ids)
print(year_range_full)
seasons = {cur_year: Season(cur_year, team_ids) for cur_year in year_range_full}
print(seasons[1999])
print(seasons.keys())
#
#
#
#
#
#| label: helper-fns
# Ties count as 0.5 win and 0.5 loss
win_vec = np.array([1, 0, 0.5])
loss_vec = np.array([0, 1, 0.5])
def compute_win_pct(record_vec):
    if np.sum(record_vec) == 0:
        # No games played yet, win pct considered 0
        return 0
    total_wins = np.dot(record_vec, win_vec)
    total_losses = np.dot(record_vec, loss_vec)
    win_pct = total_wins / (total_wins + total_losses)
    return win_pct

def compare_records(record_a, record_b):
    pct_a = compute_win_pct(record_a)
    pct_b = compute_win_pct(record_b)
    if pct_a > pct_b:
        return 1
    if pct_b > pct_a:
        return -1
    return 0
#
#
#
#
#
#| label: season-loop
all_result_data = []
for row_index, row in combined_df.iterrows():
    cur_game_id = row['game_id']
    cur_season = row['season']
    season_obj = seasons[cur_season]
    cur_week = row['week']
    cur_away = row['away_team']
    cur_home = row['home_team']
    cur_result = row['result']
    #print(cur_away, cur_home, cur_result)
    away_pre_record = season_obj.get_team_record(cur_away)
    home_pre_record = season_obj.get_team_record(cur_home)
    away_better = compare_records(away_pre_record, home_pre_record)
    if away_better > 0:
        better_team = cur_away
    elif away_better < 0:
        better_team = cur_home
    else:
        better_team = "none"
    #print(cur_away, away_pre_record, cur_home, home_pre_record, away_better)
    if cur_result < 0:
        # Away team won
        winning_team = cur_away
        away_result = np.array([1,0,0])
        home_result = np.array([0,1,0])
    elif cur_result > 0:
        # Home team won
        winning_team = cur_home
        home_result = np.array([1,0,0])
        away_result = np.array([0,1,0])
    else:
        # Tie
        winning_team = "none"
        away_result = np.array([0,0,1])
        home_result = np.array([0,0,1])
    season_obj.record_result(cur_away, away_result)
    season_obj.record_result(cur_home, home_result)
    away_post_record = season_obj.get_team_record(cur_away)
    home_post_record = season_obj.get_team_record(cur_home)
    #print(cur_away, away_post_record, cur_home, home_post_record)
    # Now we can create the results data
    result_data = {
        'game_id': cur_game_id,
        'away_pre': away_pre_record,
        'home_pre': home_pre_record,
        'better_team': better_team,
        'winning_team': winning_team,
        'better_won': (better_team != "none") and (better_team == winning_team),
        'away_result': away_result,
        'home_result': home_result,
        'away_post': away_post_record,
        'home_post': home_post_record
    }
    all_result_data.append(result_data)
#
#
#
#
#
#| label: result-df
result_df = pd.DataFrame(all_result_data)
result_df.head()
#
#
#
#
#
#| label: better-worse-df
result_comp_df = result_df[result_df['better_team'] != "none"].copy()
result_comp_df.head()
#
#
#
#
#
result_comp_df['better_won'].mean()
#
#
#
#
#
result_comp_df['season'] = result_comp_df['game_id'].apply(lambda x: int(x.split("_")[0]))
mean_by_season = result_comp_df.groupby('season')['better_won'].mean().reset_index()
mean_by_season
#
#
#
#
#
#
#
import matplotlib.pyplot as plt
import seaborn as sns
#plt.figure(figsize=(11,8))
season_plot = sns.lineplot(x='season', y='better_won', data=mean_by_season, marker='o')
plt.xticks(rotation=45, ha='right')
plt.show()
#
#
#
#
#
season_regplot = sns.regplot(x='season', y='better_won', data=mean_by_season, ci=89, title="Predictability of NFL Games, 1987-2021") #, lowess=True)
season_regplot.axhline(mean_by_season['better_won'].mean(), linestyle="dashed")
#plt.title("Predictability of NFL Games, 1987-2021")
plt.show()
#
#
#
#
#
#
#
#
#
#
#
