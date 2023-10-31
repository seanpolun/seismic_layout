import matplotlib.pyplot as plt
import numpy as np
import math
import pandas as pd
import json

class ShootParams():
    def __init__(self, input_dict):
        # self.shot_spacing = 6
        # self.phone_spacing = 2
        # self.num_16_strings = 2
        # self.num_24_strings = 4
        # self.lead_shots = 2
        # self.line_offset = 162 # to align with reflection line
        # self.total_phone_inv = (self.num_24_strings * 24) + (self.num_16_strings * 16)
        # self.tot_num_strings = self.num_16_strings + self.num_24_strings
        # self.annotation_spacing = 10
        # strings_24 = np.ones(self.num_24_strings) * 24
        # strings_16 = np.ones(self.num_16_strings) * 16
        # self.init_string_layout = np.concatenate([strings_24, strings_16])
        # self.init_string_pos = np.empty_like(self.init_string_layout)
        self.lead_shots = input_dict['lead_shots']
        self.line_offset = input_dict['line_offset']
        self.shot_spacing = input_dict['shot_spacing']
        self.phone_spacing = input_dict['phone_spacing']
        # line_length = input_dict['line_length']
        self.line_inventory = pd.read_csv(input_dict['line_inventory'], skipinitialspace=True)
        self.phone_list = self.line_inventory.iloc[:, 2]
        self.total_phone_inv = self.phone_list.sum()
        self.tot_num_strings = len(self.line_inventory.index)
        # self.first_phone_pos = input_dict['first_phone_position']
        self.annotation_spacing = input_dict['annotation_spacing']
        self.init_string_layout = self.phone_list.to_numpy()
        self.init_string_pos = np.empty_like(self.init_string_layout)
        str_geom = np.cumsum(self.init_string_layout)
        self.lead_shot_len = self.lead_shots * self.shot_spacing
        self.first_phone_pos = self.lead_shot_len
        phone_pos = self.first_phone_pos
        for i, str_num in np.ndenumerate(self.init_string_layout):
            self.init_string_pos[i] = phone_pos
            phone_pos = phone_pos + (str_num * self.phone_spacing)

        self.string_aperture = self.total_phone_inv * self.phone_spacing
        self.num_shots = math.floor(self.string_aperture / self.shot_spacing) + (2 * self.lead_shots)
        self.line_length = self.string_aperture + (2 * self.first_phone_pos)
        self.annotation_dist = np.arange(0,self.line_length, self.annotation_spacing) + self.line_offset
        moveup = self.shot_spacing / self.phone_spacing
        self.fold = self.total_phone_inv / (2 * moveup)


def main(json_input):
    with open(json_input) as in_file:
        input_json = json.load(in_file)
    inputs = input_json['input_data'][0]
    params = ShootParams(inputs)
    print(params.num_shots)
    page_x = 11 # inches
    page_y = 8.5 # inches
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
    shot_dist = np.arange(0, (params.string_aperture + (2 * params.lead_shot_len)), params.shot_spacing) + \
                params.line_offset
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
        if params.line_offset != 0:
            ax.annotate("{:.0f}".format(i + 1), (shot_x_annot[i], shot_y_annot[i]),
                        textcoords="offset points", xytext=(0, 30), horizontalalignment="center", color="b")

    num_strings = params.tot_num_strings
    colors = ["deeppink", "lime", "blue", "orange", "white", "yellow"]
    ph_spacing = params.phone_spacing
    for string in range(num_strings):
        num_phones = params.init_string_layout[string]
        first_phone_pos = params.init_string_pos[string]
        # str_color = colors[string]
        str_color = params.line_inventory.iloc[string, 1]

        ph_dist = np.arange(first_phone_pos, (first_phone_pos + ph_spacing * num_phones), ph_spacing) + \
                  params.line_offset
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

    # Add Text Box
    shot_text = "Shot Spacing = {:.1f} \n".format(params.shot_spacing)
    phone_text = "Phone Spacing = {:.1f} \n".format(params.phone_spacing)
    line_offset_text = "Line Offset = {:.1f} \n".format(params.line_offset)
    num_lead_shots = "{:.0f} OOS Shots \n".format(params.lead_shots)
    num_shots_text = "{:.0f} Shots \n".format(params.num_shots)
    first_shot_pos_txt = "First Shot @ {:.1f} \n".format(min(shot_dist))
    last_shot_pos_txt= "Last Shot @ {:.1f}".format(max(shot_dist))
    fold_text = "{:.0f} Fold \n".format(params.fold)
    annot_text = shot_text + phone_text + line_offset_text + num_lead_shots + num_shots_text + first_shot_pos_txt + \
                 last_shot_pos_txt + fold_text

    ax.text(0.9, 0.05, annot_text, transform=ax.transAxes, horizontalalignment='right', bbox=dict(facecolor='white',
                                                                                                  alpha=0.7))

    ax.grid()
    ax.set_axisbelow(True)
    plt.show()
    fig.savefig("refraction.pdf")


if __name__ == '__main__':
    json_file = "./refraction.json"
    main(json_file)
