# SimiliRaptor

Attempt to write a script to detect similar images in arbitrary image dataset.

## Current state

- Dataset: [2105 images](tests/dataset/)
- Manually detected similarities:
  - [JSON](tests/dataset_similarities.json)
  - [HTML (human readable)](tests/dataset_similarities.html)
- Code:
  - [Brute force detection script](tests/brute_force_similarities.py)
  - [Pre-selected detection function (not yet embedded in a script)](imgsimsearch/__init__.py)
