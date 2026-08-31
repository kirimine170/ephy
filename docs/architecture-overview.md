# Ephy ecosystem architecture overview

## Workspace boundary

The local workspace is a non-Git directory whose direct children are independent repositories．There is no monorepo，submodule，subtree，or nested parent repository．Each child retains its own history，remote，branch rules，tests，and release boundary．

## Responsibility map

- `ephy` owns the clone manifest，ecosystem validation，repository map，and architecture overview．It does not contain runtime code，model weights，or private personality data．
- `ephy-runtime` owns local model routing，RAG，tools，evaluation，and desktop interaction．
- `ephy-worker` defines a remote node that executes explicitly authorized jobs．It is not the existing local `apps/worker/cli.py` command．
- `ephy-physical-ci` coordinates build，flash，test，and result collection through worker boundaries．
- `ephy-cam` defines capture and ingestion contracts without storing master images．
- `ephy-model` owns training，evaluation，dataset schemas，and release recipes without storing raw sensitive datasets or model weights in Git．
- `karte` remains the canonical Markdown data application．
- `karte-renderer` is an output integration for rendered documents．
- `ephy-private` is isolated from the default workspace and all worker or device distribution paths．

The portable camera，runtime context，and accepted-photo diary flow are defined in [the camera context architecture](camera-context.md)．That document fixes cross-repository meanings while each implementation and JSON Schema remains in its owning repository．

## Relationship model

Each Ephy repository declares only its parent and direct relationships in `.ephy/project.yaml`．The meta repository validates those declarations and derives the graph．`relations.parent: null` is reserved for the `ephy` ecosystem root．

## Current implementation state

The workspace bootstrap，status reporting，and ecosystem validation are implemented．The XIAO ESP32S3 Sense manual USB capture reference and physical-CI validation boundary are implemented in their owning repositories．Portable automatic capture，short-lived permits，runtime visual context，media lifecycle，and automatic accepted-photo diary finalization are accepted or proposed designs，not current production behavior．No duration or completion percentage is inferred from these states．
