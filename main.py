import matplotlib.pyplot as plt
import numpy as np
import math
import json
import pandas as pd
import os


class ShootParams():
    def __init__(self, input_dict):
        self.shot_spacing = input_dict['shot_spacing']
        self.phone_spacing = input_dict['phone_spacing']
        line_length = input_dict['line_length']
        self.line_inventory = pd.read_csv(input_dict['line_inventory'], skipinitialspace=True)
        # self.num_16_strings = 2
        # self.num_24_strings = 4
        # self.total_phone_inv = (self.num_24_strings * 24) + (self.num_16_strings * 16)
        # self.tot_num_strings = self.num_16_strings + self.num_24_strings
        self.phone_list = self.line_inventory.iloc[:, 2]
        self.total_phone_inv = self.phone_list.sum()
        self.tot_num_strings = len(self.line_inventory.index)
        self.first_phone_pos = input_dict['first_phone_position']
        self.annotation_spacing = input_dict['annotation_spacing']
        # strings_24 = np.ones(self.num_24_strings) * 24
        # strings_16 = np.ones(self.num_16_strings) * 16
        # self.init_string_layout = np.concatenate([strings_24, strings_16])
        self.init_string_layout = self.phone_list.to_numpy()
        self.init_string_pos = np.empty_like(self.init_string_layout)
        str_geom = np.cumsum(self.init_string_layout)
        phone_pos = self.first_phone_pos
        for i, str_num in np.ndenumerate(self.init_string_layout):
            self.init_string_pos[i] = phone_pos
            phone_pos = phone_pos + (str_num * self.phone_spacing)
        relative_str_pos = str_geom / str_geom[-1]
        self.annotation_dist = np.arange(0, line_length, self.annotation_spacing)

        self.lead_shots = math.floor(self.first_phone_pos / self.shot_spacing)
        self.string_aperture = self.total_phone_inv * self.phone_spacing
        self.lead_shot_len = self.lead_shots * self.shot_spacing

        initial_roll_length = self.string_aperture + self.first_phone_pos
        rolled_length = line_length - initial_roll_length
        total_rolls = rolled_length / self.string_aperture
        roll_rem = total_rolls - math.floor(total_rolls)
        total_rolls_all = math.floor(total_rolls) + 1
        id_last_roll = np.abs(relative_str_pos - roll_rem).argmin() + 1
        rolls = np.ones_like(relative_str_pos)
        rolls = rolls * total_rolls_all
        for i in range(id_last_roll):
            rolls[i] = rolls[i] + 1
        self.rolls = rolls
        self.num_rolls = np.sum(rolls) - self.tot_num_strings
        rolled_length = np.sum(rolls * self.init_string_layout * self.phone_spacing) - self.string_aperture
        self.true_length = rolled_length + self.first_phone_pos + self.string_aperture
        self.annotation_dist = np.arange(0, self.true_length, self.annotation_spacing)
        self.rolled_length = rolled_length
        self.num_shots = math.ceil((rolled_length + self.first_phone_pos) / self.shot_spacing)

class GeophoneString():
    def __init__(self, num_phones, init_position, color, rolls, shoot_params):
        self.num_phones = num_phones
        self.num_rolls = rolls
        self.init_position = init_position
        spacing = shoot_params.phone_spacing
        self.color = color
        init_string_pos = np.arange(0, (num_phones * spacing), spacing)
        string_pos = np.array([])
        for roll in np.arange(rolls):
            new_string_pos = init_string_pos + (shoot_params.string_aperture * roll) + init_position
            string_pos = np.concatenate([string_pos, new_string_pos])
        self.string_pos = string_pos


def main(json_input):
    with open(json_input) as in_file:
        input_json = json.load(in_file)
    inputs = input_json['input_data'][0]
    params = ShootParams(inputs)
    print(params.num_rolls)
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

    shot_end = params.num_shots * params.shot_spacing
    shot_dist = np.arange(0, shot_end, params.shot_spacing)
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
    strings = np.empty(num_strings, dtype='object')
    for string in range(num_strings):
        num_phones = params.init_string_layout[string]
        first_phone_pos = params.init_string_pos[string]
        roll = params.rolls[string]
        # str_color = colors[string]
        str_color = params.line_inventory.iloc[string, 1]
        str_obj = GeophoneString(num_phones, first_phone_pos, str_color, roll,params)
        strings[string] = str_obj

        ph_dist = str_obj.string_pos
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
    fig.savefig("reflection.pdf")


if __name__ == '__main__':
    json_file = "./reflection.json"
    main(json_file)


