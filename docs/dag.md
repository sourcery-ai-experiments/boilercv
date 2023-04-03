```{mermaid}
flowchart TD
 node1["schema"]
 node2["data\rois.dvc"]
 node3["data\sources.dvc"]
 node4["update_binarized_preview"]
 node2-->node4
 node3-->node4
 node5["data\examples.dvc"]
 node6["data\samples.dvc"]
```
