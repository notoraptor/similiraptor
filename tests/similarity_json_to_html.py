import json
import os
import sys
from typing import List

OUTPUT_BASENAME = "brute_force_sim_per_img_k0_count_r2_l3x10_no_norm"
OUTPUT_JSON_PATH = os.path.join(os.path.dirname(__file__), f"{OUTPUT_BASENAME}.json")
OUTPUT_HTML_PATH = os.path.join(os.path.dirname(__file__), f"{OUTPUT_BASENAME}.html")


def _path_to_uri(filename: str):
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


def main():
    with open(OUTPUT_JSON_PATH) as file:
        groups = json.load(file)
    generate_similarity_html(groups, OUTPUT_HTML_PATH)


if __name__ == "__main__":
    main()
