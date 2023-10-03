import json
import os
import sys
from typing import List

from PIL import Image

from tests.profiling import Profiler

TEST_DIR = os.path.dirname(__file__)


class ImageUtils:
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


class SimilarityChecker:
    __slots__ = ("video_to_sim", "sim_groups")

    def __init__(self):
        with open(os.path.join(TEST_DIR, "dataset_similarities.json")) as file:
            self.sim_groups = [
                (
                    i,
                    [
                        os.path.join(TEST_DIR, "dataset", "images", basename)
                        for basename in group
                    ],
                )
                for i, group in enumerate(json.load(file))
            ]
        self.video_to_sim = {
            filename: value
            for value, filenames in self.sim_groups
            for filename in filenames
        }

    def check(self, new_sim_groups: List[List[str]]):
        video_to_sim = self.video_to_sim
        sim_groups = self.sim_groups

        new_video_to_group = {
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
            total = sum(len(videos) - 1 for _, videos in sim_groups)
            not_found = 0
            for sim_id, videos in sim_groups:
                missing_is_printed = False
                filename, *linked_filenames = videos
                for linked_filename in linked_filenames:
                    has_l = linked_filename in new_video_to_group.get(filename, ())
                    has_r = filename in new_video_to_group.get(linked_filename, ())
                    if not has_l and not has_r:
                        if not missing_is_printed:
                            print("Missing", sim_id, file=sys.stderr)
                            print("\t*", filename, file=sys.stderr)
                            missing_is_printed = True
                        print("\t ", linked_filename, file=sys.stderr)
                        not_found += 1
            found = total - not_found
            print(
                "Found",
                found,
                "/",
                total,
                f"({found * 100 / total} %)",
                file=sys.stderr,
            )


def _path_to_uri(filename: str):
    if filename.startswith("dataset/images/"):
        return filename
    filename = filename.replace("\\", "/")
    return f"file:///{filename}"


def generate_similarity_html(groups: List[List[str]], output_html_path: str):
    html = "<html><head>"
    html += """
    <style type="text/css">
    td.title {
        padding-left: 0.5rem;
        padding-right: 0.5rem;
        text-align: center;
        vertical-align: top;
        white-space: nowrap;
    }
    div.image {
        display: inline-block;
        padding: 0.25rem;
        text-align: center;
    }
    div.image div.img-title {
        font-weight: bold;
    }
    </style>
    """
    html += "</head>"
    html += "<body><table><tbody>"
    for i, group in enumerate(groups):
        html += "<tr>"
        html += f'<td class="title"><h1>Group {i}</h1></td>'
        html += "<td>"
        html += "".join(
            f'<div class="image">'
            f'<div><img src="{_path_to_uri(filename)}"/></div>'
            f'<div class="img-title">{os.path.basename(filename)[:-4]}</div>'
            f"</div>"
            for filename in group
        )
        html += "</td>"
        html += "</tr>"
    html += "<tbody></table></body>"
    html += "</html>"

    with open(output_html_path, "w") as file:
        file.write(html)

    print(
        "HTML: Saved",
        len(groups),
        f"similarity groups ({sum(len(group) for group in groups)} images) in",
        output_html_path,
        file=sys.stderr,
    )
