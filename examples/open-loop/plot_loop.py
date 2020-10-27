import numpy as np
from eyeloop.utilities.parser import Parser
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker


class Loop_parser(Parser):
    def __init__(self):
        super().__init__(animal='human')
        self.set_style()

    def custom_lower_panel_ticks(self, y, pos) -> str:
        """
        Changes brightness-ticks to 'Dark' and 'Light'.
        """

        if y == 0:
            return "Light"
        elif y == 1:
            return "Dark"

    def set_style(self):
        """
        Sets the overall style of the plots.
        """

        self.color = ["k", "orange", "b", "g", "red", "purple"]
        plt.rcParams.update({'font.family': "Arial"})
        plt.rcParams.update({'font.weight': "regular"})
        plt.rcParams.update({'axes.linewidth': 1})

    def segmentize(self, key: str) -> np.ndarray:
        """
        Segmentizes the data log based on a key signal, such as a trigger.
        """

        segments = []
        for index, entry in enumerate(self.data):
            if key in entry and entry[key] == 1:
                segments.append(index)
        return np.array(segments)

    def plot_open_loop(self, rows: int = 2, columns: int = 3) -> None:
        """
        Retrieves and parses the open-loop demo data set.
        """

        print("Select the open-loop data log demo.")
        self.load_log()

        print("Computing pupil area.")
        pupil_area = self.compute_area()

        print("Extracting monitor brightness.")
        monitor_brightness = self.extract_unique_key("open_looptest")

        print("Extracting time-stamps.")
        time = self.extract_time()

        print("Segmentizing trial based on 'trigger' entries.")
        _segments = self.segmentize("trigger")

        print("Prepares {}x{} grid plot.".format(rows, columns))
        fig = plt.figure(figsize=(5, 4))
        fig.tight_layout()
        main_grid = gridspec.GridSpec(columns, rows, hspace=1, wspace=0.3)

        margin = 50
        for grid_index, _ in enumerate(_segments):
            segment_index = grid_index * 2
            if segment_index == len(_segments) or grid_index == rows * columns:
                break

            # We extend each segment by a margin.
            # We define the pupil area and monitor brightness values based on this 'padded' segment.
            start_crop = _segments[segment_index] - margin
            end_crop = _segments[segment_index + 1] + margin
            pupil_area_segment = pupil_area[start_crop: end_crop]
            monitor_brightness_segment = monitor_brightness[start_crop: end_crop]

            # We extend the time-stamps similarly.
            # However, to align the time-line to the segment's start, we add the margin to 'time-zero'.
            time_segment = time[start_crop: end_crop]
            time_zero = time_segment[margin]
            segment_duration = [entry - time_zero for entry in time_segment]

            # We define a 2x1 grid for the pupil area plot and the monitor brightness plot.
            segment_grid = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=main_grid[grid_index], hspace=0.0,
                                                            height_ratios=[3, 2])

            # We add the upper panel and the lower panel.
            upper_panel = fig.add_subplot(segment_grid[0])
            lower_panel = fig.add_subplot(segment_grid[1], sharex=upper_panel)

            # We fix some graphical details, such as removing axes spines.
            lower_panel.axis(ymin=-.3, ymax=1.3)
            lower_panel.yaxis.set_major_formatter(mticker.FuncFormatter(self.custom_lower_panel_ticks))
            lower_panel.spines['right'].set_visible(False)
            lower_panel.yaxis.set_ticks_position('left')

            upper_panel.spines['right'].set_visible(False)
            upper_panel.spines['top'].set_visible(False)
            upper_panel.yaxis.set_ticks_position('left')
            upper_panel.xaxis.set_ticks_position('bottom')

            # Finally, we plot the data.
            upper_panel.plot(segment_duration, pupil_area_segment, self.color[grid_index], linewidth=2)
            lower_panel.plot(segment_duration, monitor_brightness_segment, "k", linewidth=1)

        print("Showing data plots.")
        plt.show()


parser = Loop_parser()
parser.plot_open_loop()
