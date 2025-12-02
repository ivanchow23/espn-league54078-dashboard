#!/usr/bin/env python
import pandas as pd
import plotly.graph_objects as go

class ManGamesLost():
    def __init__(self, espn_fantasy_api_df_csv_path):
        """ Default constructor. """
        self._daily_rosters_df = pd.read_csv(espn_fantasy_api_df_csv_path)
        self._man_games_lost_rosters_df = self._get_man_games_lost_rosters_df()

    def get_seasons(self):
        """ Returns list of valid seasons contained in the data. """
        return self._daily_rosters_df['season'].unique()

    def get_table_fig(self, season):
        """ Get a table figure of the stats for the given season. """
        # Filter for season
        season_df = self._man_games_lost_rosters_df[self._man_games_lost_rosters_df['season'] == season]

        # Data structure to store information to be used to generate table figures
        # Used later to easily translate to a dataframe table
        # Example:
        # [{'Owner': "Owner A", 'Total Games Lost': 20, 'Player': "Player A", 'Games Lost': 8},
        #  {'Owner': "",        'Total Games Lost': "", 'Player': "Player B", 'Games Lost': 7},
        #  {'Owner': "",        'Total Games Lost': "", 'Player': "Player C", 'Games Lost': 5},
        #  {'Owner': "Owner B", 'Total Games Lost': 10, 'Player': "Player D", 'Games Lost': 7},
        #  {'Owner': "",        'Total Games Lost': "", 'Player': "Player E", 'Games Lost': 3}]
        man_games_lost_table = []

        # Sort by owner's games lost
        owner_list = season_df.groupby('owner')['Games Lost'].sum().sort_values(ascending=False).index.to_list()
        for owner in owner_list:
            owner_df = season_df[season_df['owner'] == owner]
            total_games_lost = owner_df['Games Lost'].sum()

            # Sort by each player
            for i, (player, player_df) in enumerate(owner_df.sort_values('Games Lost', ascending=False).groupby('fullName', sort=False)):
                # Handle special case to append first player entry on same row as owner/total points
                if i == 0:
                    man_games_lost_table.append({'Owner': owner,
                                                 'Total Games Lost': total_games_lost,
                                                 'Player': player,
                                                 'Games Lost': player_df['Games Lost'].iloc[0]})
                else:
                    man_games_lost_table.append({'Owner': "",
                                                 'Total Games Lost': "",
                                                 'Player': player,
                                                 'Games Lost': player_df['Games Lost'].iloc[0]})

            # Add empty row for formatting/display purposes
            man_games_lost_table.append({'Owner': "", 'Total Games Lost': "", 'Player': "", 'Games Lost': ""})

        # Generate table figures for each player
        df = pd.DataFrame(man_games_lost_table)
        fig = go.Figure(data=[go.Table(header={'values': df.columns},
                                       cells={'values': [df[col].to_list() for col in df.columns]})])

        # Attempt to adjust figure height based on number of entries in table
        fig_height = 225 + (20 * len(df))
        fig.update_layout(height=fig_height)

        title_str = f"Man Games Lost (# of Games Player was Out/IR but Left on Roster) ({season})<br>"
        title_str += "Note: Goalies not starting but not injured appear in this stat for some seasons"
        fig.update_layout(title=title_str)
        return fig

    def _get_man_games_lost_rosters_df(self):
        """ Get dataframe of man games lost data derived from original raw dataframe. """
        # Filter out for when players are placed on the bench or IR
        daily_rosters_df = self._daily_rosters_df[(self._daily_rosters_df['lineupSlotId'] != 7) & (self._daily_rosters_df['lineupSlotId'] != 8)]

        # Filter for man games lost only (player is out/IR but still on the roster)
        # The pattern appears to be when applied total is 0, by GP is invalid
        # Note: Goalies not starting a game also appears with the same data pattern
        man_games_lost_rosters_df = daily_rosters_df[daily_rosters_df['appliedTotal'] == 0]
        man_games_lost_rosters_df = man_games_lost_rosters_df[man_games_lost_rosters_df['GP'].isnull()]

        # Group by owner and count each player's number of games lost
        # Re-use and rename the "appliedTotal" column
        man_games_lost_rosters_df = man_games_lost_rosters_df.groupby(['owner', 'season', 'lineupSlotId', 'fullName'])['appliedTotal'].count().reset_index()
        man_games_lost_rosters_df = man_games_lost_rosters_df.rename(columns={'appliedTotal': 'Games Lost'})

        # Rename positions
        man_games_lost_rosters_df['lineupSlotId'] = man_games_lost_rosters_df['lineupSlotId'].replace(3, "Forwards")
        man_games_lost_rosters_df['lineupSlotId'] = man_games_lost_rosters_df['lineupSlotId'].replace(4, "Defencemen")
        man_games_lost_rosters_df['lineupSlotId'] = man_games_lost_rosters_df['lineupSlotId'].replace(5, "Goalies")
        man_games_lost_rosters_df = man_games_lost_rosters_df.rename(columns={'lineupSlotId': 'position'})

        return man_games_lost_rosters_df