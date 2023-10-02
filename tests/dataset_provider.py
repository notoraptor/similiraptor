import os
from typing import List

from PIL import Image

import sys

import json
from tests.profiling import Profiler


TEST_DIR = os.path.dirname(__file__)


class Dataset:
    IMAGE_RGB_MODE = "RGB"

    @classmethod
    def open_rgb_image(cls, file_name) -> Image.Image:
        image = Image.open(file_name)
        if image.mode != cls.IMAGE_RGB_MODE:
            image = image.convert(cls.IMAGE_RGB_MODE)
        return image

    @staticmethod
    def new_rgb_image(data, width, height):
        image = Image.new("RGB", (width, height))
        image.putdata(data)
        return image

    @classmethod
    def get_image_paths(cls) -> List[str]:
        dataset_folder = os.path.join(os.path.dirname(__file__), "dataset", "images")
        paths = sorted(
            os.path.join(dataset_folder, name) for name in os.listdir(dataset_folder)
        )
        assert len(paths) == 2105
        return paths


class Checker:
    __slots__ = ("video_to_sim", "sim_groups")

    def __init__(self):
        with open(os.path.join(TEST_DIR, "dataset_similarities.json")) as file:
            self.sim_groups = list(enumerate(json.load(file)))
        self.video_to_sim = {
            filename: value
            for value, filenames in self.sim_groups
            for filename in filenames
        }

    def check(self, new_sim_groups: List[List[str]]):
        video_to_sim = self.video_to_sim
        sim_groups = self.sim_groups

        video_to_group = {
            filename: group for group in new_sim_groups for filename in group
        }

        nb_similar_videos = sum(len(videos) for _, videos in sim_groups)
        print("Similarities", len(sim_groups), file=sys.stderr)
        print("Similar videos", nb_similar_videos, file=sys.stderr)
        if new_sim_groups:
            nb_new_similar_videos = sum(len(group) for group in new_sim_groups)
            nb_new_similar_groups = len(new_sim_groups)
            print("New similarities", nb_new_similar_groups, file=sys.stderr)
            print("New similar videos", nb_new_similar_videos, file=sys.stderr)

        with Profiler("Check new sim groups"):
            for group in new_sim_groups:
                old_sims = {video_to_sim.get(filename, -1) for filename in group}
                if len(old_sims) != 1:
                    print("Bad group", file=sys.stderr)
                    for filename in group:
                        print(
                            "\t",
                            video_to_sim.get(filename, -1),
                            filename,
                            file=sys.stderr,
                        )
                else:
                    (sim,) = list(old_sims)
                    if sim == -1:
                        print("New group", file=sys.stderr)
                        for filename in group:
                            print("\t", filename, file=sys.stderr)

        with Profiler("Check expected similarities"):
            for sim_id, videos in sim_groups:
                missing_is_printed = False
                filename, *linked_filenames = videos
                for linked_filename in linked_filenames:
                    has_l = linked_filename in video_to_group.get(filename, ())
                    has_r = filename in video_to_group.get(linked_filename, ())
                    if not has_l and not has_r:
                        if not missing_is_printed:
                            print("Missing", sim_id, file=sys.stderr)
                            print("\t*", filename, file=sys.stderr)
                            missing_is_printed = True
                        print("\t ", linked_filename, file=sys.stderr)
