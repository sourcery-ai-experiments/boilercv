```{mermaid}
flowchart TD
 node1["binarized_preview"]
 node2["contours"]
 node3["correlations"]
 node4["data\rois.dvc"]
 node5["data\sources.dvc"]
 node6["fill"]
 node7["filled_preview"]
 node8["gray_preview"]
 node9["lifetimes"]
 node10["tracks"]
 node11["unobstructed"]
 node2-->node6
 node2-->node11
 node3-->node9
 node4-->node1
 node5-->node1
 node5-->node2
 node5-->node6
 node5-->node7
 node5-->node8
 node6-->node7
 node10-->node9
 node11-->node10
 node12["data\examples.dvc"]
 node13["data\samples.dvc"]
 style node3 fill:#FFE18E
 style node9 fill:#FFE18E
 style node10 fill:#FFE18E
 style node11 fill:#FFE18E
```
