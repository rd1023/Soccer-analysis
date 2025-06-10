import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_heatmap(df, player_name):
    df_player = df[df["Player"] == player_name]
    coords = df_player["Location"].dropna().str.extract(r'(\d+),(\d+)').astype(float)
    if coords.empty:
        return None
    fig, ax = plt.subplots()
    sns.kdeplot(x=coords[0], y=coords[1], fill=True, ax=ax, cmap='coolwarm', bw_adjust=0.5)
    ax.set_title(f"Heatmap for {player_name}")
    ax.set_xlim(0, 400)
    ax.set_ylim(0, 300)
    return fig
