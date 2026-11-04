 

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

from busplanner.calculations.imports import convert_time_to_minutes


def plot_gantt(df, save_path=None):
    """

    plot a Gantt chart of the bus schedule

        Parameters:
    
        df: pandas DataFrame with columns 'bus', 'start time', 'end time', 'activity'
        save_path: optional path to save the figure (SET TO FILE PATH TO SAVE)
    
        Returns:
        fig: matplotlib figure object
        
    """

    plot_df = df.copy()
    for col in ['start time', 'end time']:
        if col in plot_df.columns:
            plot_df[col] = convert_time_to_minutes(plot_df[col])

    plot_df['activity'] = (
        plot_df['activity']
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(' trip', '', regex=False)
    )

    # COLOR TABLE 
    colors = {'service': '#2a6fb0',   # blue
          'material': '#e08a1e',  # orange
          'charging': '#3a9a5b',  # green
          'idle': '#d0d0d0'}      # light grey

    fig,ax =  plt.subplots(figsize=(16,6))

    width = plot_df['end time'] - plot_df['start time'] # width of block
    color_values = plot_df['activity'].map(colors).fillna('#d0d0d0')

    ax.barh(
             plot_df['bus'], width,
             left=plot_df['start time'],
             color=color_values,
             )

    # PARAMS

    ax.invert_yaxis() # Put bus 1 on top
    ax.set_yticks(sorted(plot_df['bus'].unique()))
    ticks = list(range(0, int(plot_df['end time'].max()) + 60, 60))
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{(m // 60) % 24:02d}:00" for m in ticks])
    ax.set_xlabel("Time of day")
    ax.set_ylabel("Bus")
    plt.setp(ax.get_xticklabels(), rotation=45)
    ax.grid(axis='x', alpha=0.3)

    # LEGEND

    ax.legend(handles=[Patch(color=c, label=a) for a, c in colors.items()])


    ax.barh(plot_df['bus'], width, left=plot_df['start time'],
        color=color_values,
        height=0.6,            # thinner bars, with gaps between bus rows
        edgecolor='white',     # thin separator so neighbouring bars stay distinct
        linewidth=0.5)

    ax.spines[['top', 'right']].set_visible(False)   # remove the box around the plot
    ax.set_title(f"Bus schedule ({plot_df['bus'].nunique()} buses)", fontsize=28, loc='left', weight='bold', pad=20)
    ax.tick_params(labelsize=9)

    if save_path:
        fig.savefig(save_path, bbox_inches='tight', dpi=300)

    return fig



