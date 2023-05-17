# boilercv

[![DOI](https://zenodo.org/badge/503551174.svg)](https://zenodo.org/badge/latestdoi/503551174)

Computer vision routines suitable for nucleate pool boiling bubble analysis. See the [documentation](https://blakenaccarato.github.io/boilercv/) for more detail.

## Data process graph

Graph of the data process, automatically derived from the code itself.

```mermaid
flowchart TD
 node1["schema"]
 node2["binarized_preview"]
 node3["contours"]
 node4["data\rois.dvc"]
 node5["data\sources.dvc"]
 node6["fill"]
 node7["filled_preview"]
 node8["gray_preview"]
 node3-->node6
 node4-->node2
 node5-->node2
 node5-->node3
 node5-->node6
 node5-->node7
 node5-->node8
 node6-->node7
 node9["data\examples.dvc"]
 node10["data\samples.dvc"]
```

## Example

Detected contours are highlighted in the example below. See the [documentation](https://blakenaccarato.github.io/boilercv/) for detail on the representative dataset used to generate this example, available in `tests/data`.

### Highlighted contours

Overlay of the external contours detected in one frame of a high-speed video. Represents output from the "fill" step of the data process.

![Bubbles highlighted with different colors](docs/_static/multicolor.png)

## Coming soon

Detailed project architecture and a proper tutorial for forking/cloning this repository and running the pipeline on your own data.
