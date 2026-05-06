#!/usr/bin/env python
import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DRAFT_DATA_CSV_PATH = os.path.join(SCRIPT_DIR, "..", "docs", "data", "draft_df.csv")

class DraftStats():
    def __init__(self):
        """ Default constructor. """
        self._draft_df = pd.read_csv(DRAFT_DATA_CSV_PATH)
        self._draft_df = self._process_data(self._draft_df)

    def get_unique_owners(self):
        """ Get number of unique owners in the draft. """
        return sorted(self._draft_df['Owner Name'].unique())

    def get_draft_birth_country_data(self, owner, season=None):
        """ Get data for owner's draft birth countries for the given season. """
        df = self._draft_df
        if season is not None:
            df = df[df['Season'] == season]

        owner_df = df[df['Owner Name'] == owner]
        series = owner_df['Player Birth Country'].value_counts()
        return series

    def get_draft_player_age_data(self, owner, season=None):
        """ Get data for owner's draft player age for the given season. """
        df = self._draft_df
        if season is not None:
            df = df[df['Season'] == season]

        owner_df = df[df['Owner Name'] == owner]
        series = owner_df['Player Age'].value_counts()
        return series

    def get_draft_player_conference_data(self, owner, season=None):
        """ Get data for owner's draft conference for the given season. """
        df = self._draft_df
        if season is not None:
            df = df[df['Season'] == season]

        owner_df = df[df['Owner Name'] == owner]
        series = owner_df['Conference'].value_counts()
        return series

    def get_owner_draft_position_data(self, owner):
        """ Get data for an owner's draft position for all seasons. """
        owner_df = self._draft_df[self._draft_df['Owner Name'] == owner].copy()
        first_round_df = owner_df[owner_df['Round Number'] == 1]
        return first_round_df['Draft Number'].apply(self._number_ordinal).value_counts()

    def get_owner_top_drafted_players(self, owner, num_players=5):
        """ Gets top drafted players of the given owner. """
        owner_df = self._draft_df[self._draft_df['Owner Name'] == owner].copy()
        owner_df = owner_df.dropna(subset=['Player ID'])
        owner_df['Player ID'] = owner_df['Player ID'].astype(int)

        player_counts = owner_df.groupby(['Player', 'Player ID']).size().reset_index(name='Count')
        df = player_counts.sort_values('Count', ascending=False).reset_index(drop=True).head(num_players)
        return df.to_dict('records')

    def get_owner_top_drafted_teams(self, owner, num_teams=5):
        """ Gets top drafted teams of the given owner. """
        owner_df = self._draft_df[self._draft_df['Owner Name'] == owner].copy()
        team_counts = owner_df['Team'].value_counts().reset_index()
        team_counts.columns = ['Team', 'Count']
        df = team_counts.sort_values('Count', ascending=False).reset_index(drop=True).head(num_teams)
        return df.to_dict('records')

    def _process_data(self, draft_df):
        """ Apply some data processing to the data. """
        df = draft_df
        df['Player Birth Country'] = df['Player Birth Country'].apply(self._update_countries_code)
        return df

    def _update_countries_code(self, country_code):
        """ Helper function to update country codes for stats purposes. """
        if country_code == "RUS" or country_code == "USSR":
            return "RUS/USSR"

        # Keep as-is
        return country_code

    def _number_ordinal(self, val):
        """ Simple function to convert an integer to a "numerical ordinal"
            string. Example: 1, 2, 3, 4 -> 1st, 2nd, 3rd, 4th. """
        if val == 1:
            return "1st"
        elif val == 2:
            return "2nd"
        elif val == 3:
            return "3rd"
        else:
            return f"{val}th"