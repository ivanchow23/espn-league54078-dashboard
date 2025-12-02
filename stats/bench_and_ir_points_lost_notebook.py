""" Finds the points lost per owner per season due to leaving a player
    on IR or the bench. """
# %%
# Imports
#!/usr/bin/env python
import os
import pandas as pd

# %%
# Configurations
daily_rosters_df_path = os.path.join("..", "docs", "data", "espn_fantasy_api_daily_rosters_df.csv")
daily_rosters_df = pd.read_csv(daily_rosters_df_path)

# %%
# Calculate points lost leaving player on IR/bench per season for each owner
for season, season_df in daily_rosters_df.groupby('season'):
    for owner, owner_df in season_df.groupby('owner'):
        # Filter for bench slots, which seems to be ID = 7
        bench_df = owner_df[owner_df['lineupSlotId'] == 7]
        bench_pts = int(bench_df['appliedTotal'].sum())

        # Filter for IR slots, which seems to be ID = 8
        ir_df = owner_df[owner_df['lineupSlotId'] == 8]
        ir_pts = int(ir_df['appliedTotal'].sum())

        # Print totals
        print(f"{season}: {owner} left {bench_pts + ir_pts} points on the bench/IR (bench: {bench_pts} IR: {ir_pts})")

        # Break down bench points
        bench_pts = []
        for player, player_df in bench_df.groupby('fullName'):
            bench_pts.append({'player': player,
                              'gp': int(player_df['GP'].sum()),
                              'pts': int(player_df['appliedTotal'].sum())})

        # Sort by descending points for printing purposes
        bench_pts = sorted(bench_pts, key=lambda d: d['pts'], reverse=True)
        for pts in bench_pts:
            if pts['pts'] != 0:
                print(f"{pts['player']}: {pts['pts']} points in {pts['gp']} games ({round(pts['pts'] / pts['gp'], 2)} pts/game) (bench)")

        # Break down IR points
        ir_pts = []
        for player, player_df in ir_df.groupby('fullName'):
            ir_pts.append({'player': player,
                           'gp': int(player_df['GP'].sum()),
                           'pts': int(player_df['appliedTotal'].sum())})

        # Sort by descending points for printing purposes
        ir_pts = sorted(ir_pts, key=lambda d: d['pts'], reverse=True)
        for pts in ir_pts:
            if pts['pts'] != 0:
                print(f"{pts['player']}: {pts['pts']} points in {pts['gp']} games ({round(pts['pts'] / pts['gp'], 2)} pts/game) (IR)")

        # Formatting purposes
        print()