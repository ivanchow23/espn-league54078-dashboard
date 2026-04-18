#!/usr/bin/env python
import os
import pandas as pd

DRAFT_DATA_CSV_PATH = os.path.join("..", "docs", "data", "draft_df.csv")

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