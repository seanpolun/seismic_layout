import matplotlib.pyplot as plt
import numpy as np
import math

class ShootParams():
    def __init__(self):
        self.shot_spacing = 4
        self.num_shots_side = 8
        self.phone_spacing = 6
        self.num_16_strings = 2
        self.num_24_strings = 4
        self.total_phone_inv = (self.num_24_strings * 24) + (self.num_16_strings * 16)
        self.tot_num_strings = self.num_16_strings + self.num_24_strings
        self.annotation_spacing = 10
        strings_24 = np.ones(self.num_24_strings) * 24
        strings_16 = np.ones(self.num_16_strings) * 16
        self.init_string_layout = np.concatenate([strings_24, strings_16])
        self.init_string_pos = np.empty_like(self.init_string_layout)
        str_geom = np.cumsum(self.init_string_layout)
        self.lead_shot_len = self.num_shots_side * self.shot_spacing
        self.first_phone_pos = self.lead_shot_len
        phone_pos = self.first_phone_pos
        for i, str_num in np.ndenumerate(self.init_string_layout):
            self.init_string_pos[i] = phone_pos
            phone_pos = phone_pos + (str_num * self.phone_spacing)

        self.string_aperture = self.total_phone_inv * self.phone_spacing

        self.num_shots = 2 * self.num_shots_side
        self.line_length = self.string_aperture + (2 * self.first_phone_pos)
        self.annotation_dist = np.arange(0,self.line_length, self.annotation_spacing)

def main():
    params = ShootParams()
    print(params.num_shots)
    page_x = 17 # inches
    page_y = 11 # inches
    x_scale = 1 / 12 # inch per m
    x_spacing = 2
    page_margin = 0.5 # inches
    plot_x_max = (page_x - (2*page_margin)) / x_scale
    plot_y_max = page_y - (2*page_margin)
    y_margin_ratio = page_margin / page_y
    x_margin_ratio = page_margin / page_x
    ratio_wid = 1 - (2*x_margin_ratio)
    ratio_h = 1 - (2*y_margin_ratio)

    fig = plt.figure(figsize=(page_x, page_y), frameon=False, dpi=150)
    ax = fig.add_axes([x_margin_ratio, y_margin_ratio, ratio_wid, ratio_h])

    ax.set_xlim(-10, plot_x_max + 10)
    ax.set_ylim(-0.5, plot_y_max + 0.5)
    ax.set_xticks(np.arange(0, plot_x_max, x_spacing))
    ax.set_yticks(np.arange(0, 10))
    ax.axes.xaxis.set_ticklabels([])
    ax.axes.yaxis.set_ticklabels([])
    ax.set_frame_on(False)

    # Dist Annotation
    dist_annot = params.annotation_dist
    dist_x = np.mod(dist_annot, plot_x_max)
    dist_y = plot_y_max - np.floor(dist_annot / plot_x_max)
    for i, annot in enumerate(dist_annot):
        ax.annotate("{:.1f}".format(annot), (dist_x[i], dist_y[i]), textcoords="offset points", xytext=(0, 20),
                    horizontalalignment="center", color="k", arrowprops={'arrowstyle': '-'})

    # Plot shots
    shot_end1 = params.num_shots_side * params.shot_spacing
    shot_start2 = params.string_aperture + params.first_phone_pos
    shot_end2 = shot_start2 + shot_end1
    shot_dist1 = np.arange(0, shot_end1, params.shot_spacing)
    shot_dist2 = np.arange(shot_start2, shot_end2, params.shot_spacing)
    shot_dist = np.concatenate([shot_dist1, shot_dist2])
    shot_x = np.mod(shot_dist, plot_x_max)
    shot_y = plot_y_max - np.floor(shot_dist / plot_x_max)
    shot_annot_subsample = 1
    shot_dist_annot = (shot_dist[0::shot_annot_subsample] / params.shot_spacing) + 1
    # shot_dist_annot = params.annot_line_dist
    shot_x_annot = shot_x[0::shot_annot_subsample]
    shot_y_annot = shot_y[0::shot_annot_subsample]


    ax.scatter(shot_x, shot_y, c="r", marker="o")
    for i, shot in enumerate(shot_dist_annot):
        ax.annotate("{:.0f}".format(shot), (shot_x_annot[i],shot_y_annot[i]), textcoords="offset points", xytext=(0, 10),
                    horizontalalignment="center", color="r")
        # ax.annotate("{:.1f}".format((shot - 1)*params.shot_spacing), (shot_x_annot[i], shot_y_annot[i]),
        #             textcoords="offset points", xytext=(0, 20), horizontalalignment="center", color="k")

    num_strings = params.tot_num_strings
    colors = ["deeppink", "lime", "blue", "orange", "white", "yellow"]
    ph_spacing = params.phone_spacing
    for string in range(num_strings):
        num_phones = params.init_string_layout[string]
        first_phone_pos = params.init_string_pos[string]
        str_color = colors[string]

        ph_dist = np.arange(first_phone_pos, (first_phone_pos + ph_spacing * num_phones), ph_spacing)
        ph_x = np.mod(ph_dist, plot_x_max)
        ph_y = plot_y_max - np.floor(ph_dist / plot_x_max) - 0.25
        ax.scatter(ph_x, ph_y, c=str_color, marker="v", edgecolor="k", linewidths=0.5)

    # Dist Annotation
    dist_annot = params.annotation_dist
    dist_x = np.mod(dist_annot, plot_x_max)
    dist_y = plot_y_max - np.floor(dist_annot / plot_x_max)
    for i, annot in enumerate(dist_annot):
        ax.annotate("{:.1f}".format(annot), (dist_x[i], dist_y[i]), textcoords="offset points", xytext=(0, 20),
                    horizontalalignment="center", color="k")


    ax.grid()
    ax.set_axisbelow(True)
    plt.show()
    fig.savefig("refraction.pdf")


if __name__ == '__main__':
    main()