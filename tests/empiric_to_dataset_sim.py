import json
import os

from imgsimsearch.graph import Graph
from tests.dataset import Dataset
from tests.utilities import TEST_DIR, generate_similarity_html


def main():
    empiric_path = os.path.join(TEST_DIR, "empiric_similarities.json")
    with open(empiric_path) as file:
        empiric_data = json.load(file)
    image_paths = Dataset.get_image_paths()
    basename_to_path = {
        os.path.basename(path)[:-4]: os.path.basename(path) for path in image_paths
    }
    assert len(basename_to_path) == len(image_paths)
    graph = Graph()
    for group in empiric_data:
        path, *links = group
        for link in links:
            graph.connect(path, link)
    groups = sorted(
        (sorted(group) for group in graph.pop_groups() if len(group) > 1),
        key=lambda g: g[0],
    )
    dataset_sim = []
    for group in groups:
        group_paths = [basename_to_path[name] for name in group]
        assert len(group_paths) == len(group)
        dataset_sim.append(group_paths)
    dataset_sim_path = os.path.join(TEST_DIR, "dataset_similarities.json")
    dataset_sim_html = os.path.join(TEST_DIR, "dataset_similarities.html")
    with open(dataset_sim_path, "w") as file:
        json.dump(dataset_sim, file, indent=1)
    generate_similarity_html(
        [[f"dataset/images/{basename}" for basename in group] for group in dataset_sim],
        dataset_sim_html,
    )


if __name__ == "__main__":
    main()
