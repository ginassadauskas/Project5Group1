 

import matplotlib.pyplot as plt
from busplanner.calculations.improver.main import df_schedule
from matplotlib.patches import Patch


def plot_gantt(df, save_path=None):
    """

    plot a Gantt chart of the bus schedule

        Parameters:
    
        df: pandas DataFrame with columns 'bus', 'start time', 'end time', 'activity'
        save_path: optional path to save the figure (SET TO FILE PATH TO SAVE)
    
        Returns:
        fig: matplotlib figure object
        
    """

    # COLOR TABLE 
    colors = {'service': '#2a6fb0',   # blue
          'material': '#e08a1e',  # orange
          'charging': '#3a9a5b',  # green
          'idle': '#d0d0d0'}      # light grey

    fig,ax =  plt.subplots(figsize=(16,6))

    width = df['end time'] - df['start time'] # width of block


    ax.barh(
             df['bus'], width,
             left=df['start time'],
             color=df['activity'].map(colors),
             
             )

    # PARAMS

    ax.invert_yaxis() # Put bus 1 on top
    ax.set_yticks(sorted(df['bus'].unique()))
    ticks = list(range(0, int(df['end time'].max()) + 60, 60))
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{(m // 60) % 24:02d}:00" for m in ticks])
    ax.set_xlabel("Time of day")
    ax.set_ylabel("Bus")
    plt.setp(ax.get_xticklabels(), rotation=45)
    ax.grid(axis='x', alpha=0.3)

    # LEGEND

    ax.legend(handles=[Patch(color=c, label=a) for a, c in colors.items()])


    ax.barh(df['bus'], width, left=df['start time'],
        color=df['activity'].map(colors),
        height=0.6,            # thinner bars, with gaps between bus rows
        edgecolor='white',     # thin separator so neighbouring bars stay distinct
        linewidth=0.5)

    ax.spines[['top', 'right']].set_visible(False)   # remove the box around the plot
    ax.set_title("Bus schedule (15 buses)", fontsize=28, loc='left', weight='bold', pad=20)
    ax.tick_params(labelsize=9)

    if save_path:
        fig.savefig(save_path, bbox_inches='tight', dpi=300)

    return fig

plot_gantt(df_schedule)
