"""Load in some data and create an activity plot animation.
The data was created using the threading module and provides histograms
of function calls vs time in nanoseconds for each thread"""

import pandas as pd
import time
from tqdm import tqdm as tqdm
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('dark_background')
plt.rcParams['font.size'] = 16


if __name__ == "__main__":
    # Load data
    data = pd.read_pickle("data_to_plot.pkl")
    data = data.reset_index().drop(labels=[
        "module", "total threads"], axis=1).set_index(["thread", "time (ns)"])
    data.sort_index(inplace=True)
    data.loc[:, "Activity"] = data.loc[:, "fn calls"] > 0

    # Plot params
    NROWS = 3
    NFRAMES_START = 0
    NFRAMES_STOP = 200 # 3600 can take over an hour to complete....
    NFRAMES_TOTAL = 3600 # 3600 can take over an hour to complete....

    # Useful quantities
    NTHREADS = data.index.levels[0].size

    # get time data
    t = data.index.levels[1].unique()
    dt = t[1] - t[0]

    # split time into suitable chunks
    t_lims = [(i*t[-1]/NROWS, (i+1)*t[-1]/NROWS)
              for i in range(0, NROWS)]

    timer0 = time.perf_counter()

    for frame in tqdm(range(NFRAMES_START, NFRAMES_STOP), leave=False, desc="frame"):  # animation frames
        t_curr = t[-1]*frame/(NFRAMES_TOTAL-1)  # current time to plot upto

        # create the plot
        fig, axs = plt.subplots(figsize=(16, 8), nrows=NROWS,
                                constrained_layout=True, sharey=True)
        fig.suptitle(f"t = {t_curr/1E6:.0f} ms")

        for ax, t_lim in zip(axs, t_lims):  # loop over each axis

            for thread, df0 in data.groupby("thread"):  # loop over each thread
                df0 = df0.loc[thread]
                _xy = df0.loc[t_lim[0]:t_lim[1], "Activity"]
                # just set the values to false that we don't plot
                _xy.loc[_xy.index > t_curr] = False
                _x = _xy.index.values/1E6
                _y = _xy.values
                # add red current line time
                if t_curr >= t_lim[0] and t_curr < t_lim[1]:
                    ax.axvline(x=t_curr/1E6, color="tab:red")
                if t_curr >= t_lim[0]:
                    ax.fill_between(
                        _x, thread, thread+_y, label=f"thread {thread}")

            # grid lines, limits, and ticks
            ax.grid(axis="y", alpha=0.1)
            ax.set_ylim([-0.1, NTHREADS+0.1])
            ax.set_yticks(np.arange(0, NTHREADS+1, 1))
            ax.set_yticklabels(
                np.arange(0, NTHREADS+1, 1, dtype=np.int))
            ax.set_xlim(np.array(t_lim)/1E6)

        axs[-1].set(xlabel="time (ms)")

        # legend
        axs[0].legend(bbox_to_anchor=(0.5, 1),
                      ncol=8,
                      loc="lower center", fontsize=12)

        fig.savefig(
            f"frames/frame_{frame:04.0f}.png", dpi=150)
        plt.close(fig)

    timer1 = time.perf_counter()
    NFRAMES = NFRAMES_STOP-NFRAMES_START
    deltat = timer1-timer0
    print(
        f"\nGenerated {NFRAMES} frames in {deltat:.1f} "
        f"seconds ({NFRAMES/deltat:.1f} FPS)")
