import json
import os
import sys
from typing import List

OUTPUT_JSON_PATH = os.path.join(
    os.path.dirname(__file__), "brute_force_similarities.json"
)
OUTPUT_HTML_PATH = os.path.join(
    os.path.dirname(__file__), "brute_force_similarities.html"
)


def _path_to_uri(filename: str):
    filename = filename.replace("\\", "/")
    return f"file:///{filename}"


def generate_similarity_html(groups: List[List[str]]):
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

    with open(OUTPUT_HTML_PATH, "w") as file:
        file.write(html)

    print(
        "Saved",
        len(groups),
        f"similarity groups ({sum(len(group) for group in groups)} images) in HTML at",
        OUTPUT_JSON_PATH,
        file=sys.stderr,
    )


def main():
    with open(OUTPUT_JSON_PATH) as file:
        groups = json.load(file)
    generate_similarity_html(groups)


if __name__ == "__main__":
    main()
