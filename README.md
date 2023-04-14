# boilercv

[![DOI](https://zenodo.org/badge/503551174.svg)](https://zenodo.org/badge/latestdoi/503551174)

Computer vision routines suitable for nucleate pool boiling bubble analysis. See the [documentation](https://blakenaccarato.github.io/boilercv/) for more detail. Currently, `xarray` must be installed manually if installing as `pip install boilercv`. I intend to bundle a small example dataset to exhibit the usage of this package on arbitrary data, but this is not currently done.

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

## Highlighted contours

Overlay of the external contours detected in one frame of a high-speed video. Represents output from the "fill" step of the data process.

![Bubbles highlighted with different colors](docs/_static/multicolor.png)
