#!/usr/bin/env python
from collections import Counter
import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH = os.path.join(SCRIPT_DIR, "..", "docs", "data", "espn_fantasy_api_daily_rosters_df.csv")

class RosterChangeStats():
    def __init__(self):
        """ Default constructor. """
        self._daily_rosters_df = pd.read_csv(ESPN_FANTASY_API_DAILY_ROSTERS_CSV_PATH)

    def get_players_multiple_added_stats_all_owners(self, season):
        """ Returns stats of players that were added to the roster multiple times for all owners
            for a given season. Note: Player being on the initial roster and then re-added after
            being dropped will show up in this list.

        Returns:
            DataFrame with columns [Day Range, Player Name, Player ID, <stats>]
        """
        season_df = self._daily_rosters_df[self._daily_rosters_df['season'] == season]
        df = pd.DataFrame()
        for owner in season_df['owner'].unique():
            ret_df = self.get_players_multiple_added_stats(owner, season)
            if ret_df.empty:
                continue

            ret_df['Owner'] = owner
            df = pd.concat([df, ret_df])
        return df

    def get_players_multiple_added_stats(self, owner, season):
        """ Returns stats of players that were added to the roster multiple times for a given
            owner and season. Note: Player being on the initial roster and then re-added after
            being dropped will show up in this list.

        Returns:
            DataFrame with columns [Day Range, Player Name, Player ID, <stats>]
        """
        multiple_players_added_list = self.get_players_multiple_added_list(owner, season)
        multiple_players_added_df = pd.DataFrame(multiple_players_added_list)
        season_df = self._daily_rosters_df[self._daily_rosters_df['season'] == season]
        owner_df = season_df[season_df['owner'] == owner]

        if len(multiple_players_added_df) == 0:
            return pd.DataFrame()

        # Group changes by player
        results = []
        for (player_name, player_id), player_df in multiple_players_added_df.groupby(['Player Name', 'Player ID']):
            # Sort changes by scoring period
            player_df = player_df.sort_values('Scoring Period ID').reset_index(drop=True)

            # Get player's daily roster data
            player_daily_roster_df = owner_df[(owner_df['fullName'] == player_name) & (owner_df['id'] == player_id)].copy()
            max_scoring_period = int(player_daily_roster_df['scoringPeriodId'].max())

            # Generate scoring period ranges based on change types
            ranges = self._generate_scoring_period_id_day_ranges(player_df, max_scoring_period)

            # Calculate stats for each range
            for start_period, end_period in ranges:
                range_daily = player_daily_roster_df[
                    (player_daily_roster_df['scoringPeriodId'] >= start_period) &
                    (player_daily_roster_df['scoringPeriodId'] <= end_period)
                ]

                if len(range_daily) > 0:
                    gp = range_daily['GP'].sum()
                    pts = range_daily['appliedTotal'].sum()
                    pts_per_gp = pts / gp if gp > 0 else 0

                    results.append({
                        'Day Range': f"{start_period}-{end_period}",
                        'Player Name': player_name,
                        'Player ID': int(player_id),
                        'GP': int(gp),
                        'PTS': round(pts, 2),
                        'P/GP': round(pts_per_gp, 1)
                    })

        return pd.DataFrame(results)

    def get_players_multiple_added_list(self, owner, season):
        """ Returns a list of dictionaries of players that were added to the roster multiple
            times for a given owner and season. Note: Player being on the initial roster and
            then re-added after being dropped will show up in this list. """
        multiple_changes_list = self.get_players_multiple_roster_changes_list(owner, season)
        if len(multiple_changes_list) == 0:
            return []

        # Filter for players that either:
        # - Was on the initial roster and then added again after being dropped, or
        # - Was added to the roster multiple times (not counting the initial roster)
        multiple_add_list = []

        df = pd.DataFrame(multiple_changes_list)
        for _, player_df in df.groupby(['Player Name', 'Player ID']):
            # Keep player data that could either have at least 3 entries:
            # - Initial Roster, Dropped, Added, etc., or
            # - Added, Dropped, Added, etc.
            if len(player_df) >= 3:
                multiple_add_list = multiple_add_list + player_df.to_dict('records')

        return multiple_add_list

    def get_players_multiple_roster_changes_list(self, owner, season):
        """ Returns a list of dictionaries of players that were involved with multiple
            roster changes for a given owner and season. """
        roster_change_data = self.get_roster_change_list(owner, season)

        # Count (Player Name, Player ID) pairs
        counts = Counter((d['Player Name'], d['Player ID']) for d in roster_change_data)

        # Extract only duplicates
        return [d for d in roster_change_data
                if counts[(d['Player Name'], d['Player ID'])] > 1]

    def get_roster_change_list(self, owner, season):
        """ Returns a list of dictionaries of players and which scoring period
            they were added/dropped to/from the roster for the given owner
            and season. """
        season_df = self._daily_rosters_df[self._daily_rosters_df['season'] == season]
        owner_df = season_df[season_df['owner'] == owner]
        owner_df = owner_df.sort_values(by='scoringPeriodId')

        # Get unique scoring periods in order
        scoring_periods = sorted(owner_df['scoringPeriodId'].unique())

        # Handle case where the first scoring period is technically a new roster addition for drafted players
        new_additions = []
        first_period_players = owner_df[owner_df['scoringPeriodId'] == scoring_periods[0]][['fullName', 'id']].drop_duplicates()
        for _, row in first_period_players.iterrows():
            new_additions.append({
                'Scoring Period ID': int(scoring_periods[0]),
                'Player Name': row['fullName'],
                'Player ID': int(row['id']),
                'Change Type': 'Initial Roster'
            })

        # Compare each period with the previous one
        for i in range(1, len(scoring_periods)):
            current_period = scoring_periods[i]
            previous_period = scoring_periods[i - 1]

            # Get players in current and previous periods
            current_players = owner_df[owner_df['scoringPeriodId'] == current_period][['fullName', 'id']]
            previous_players = owner_df[owner_df['scoringPeriodId'] == previous_period][['fullName', 'id']]
            current_ids = set(current_players['id'].values)
            previous_ids = set(previous_players['id'].values)

            # Find new players (in current but not in previous)
            new_player_ids = current_ids - previous_ids

            # Find removed players (in previous but not current)
            dropped_player_ids = previous_ids - current_ids

            # Get details of new players
            for player_id in new_player_ids:
                player_info = current_players[current_players['id'] == player_id].iloc[0]
                new_additions.append({
                    'Scoring Period ID': int(current_period),
                    'Player Name': player_info['fullName'],
                    'Player ID': int(player_info['id']),
                    'Change Type': 'Added'
                })

            # Get details of dropped players
            for player_id in dropped_player_ids:
                player_info = previous_players[previous_players['id'] == player_id].iloc[0]
                new_additions.append({
                    'Scoring Period ID': int(current_period),
                    'Player Name': player_info['fullName'],
                    'Player ID': int(player_info['id']),
                    'Change Type': 'Dropped'
                })

        return new_additions

    def _generate_scoring_period_id_day_ranges(self, player_df, max_period):
        """ Generate list of (start_period, end_period) tuples based on roster changes.

        Logic:
        - Initial Roster starts at the first scoring period until first Dropped
        - After a Dropped, if there's an Added, new range starts from Added
        - Ranges continue until Dropped or end of season (max_period)
        """
        ranges = []
        changes_list = player_df.to_dict('records')

        i = 0
        while i < len(changes_list):
            change = changes_list[i]
            start_period = change['Scoring Period ID']

            # Find the end of this range (either at next Dropped or at max period)
            if change['Change Type'] in ['Initial Roster', 'Added']:
                # Look for the next Dropped
                end_period = max_period  # Default to max period

                for j in range(i + 1, len(changes_list)):
                    if changes_list[j]['Change Type'] == 'Dropped':
                        # -1 because "Dropped" means they are no longer on the roster on this day
                        end_period = changes_list[j]['Scoring Period ID'] - 1
                        break

                # Handle case where player ends with "Added" - use max period
                if i == len(changes_list) - 1 and change['Change Type'] == 'Added':
                    end_period = max_period

                ranges.append((start_period, end_period))
                i += 1
            else:
                # Skip Dropped entries as they mark the end of a range
                i += 1

        return ranges

if __name__ == "__main__":
    r = RosterChangeStats()
    ret = r.get_players_multiple_added_stats_all_owners(20252026)
    print(ret)