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

## Relationship model

Each Ephy repository declares only its parent and direct relationships in `.ephy/project.yaml`．The meta repository validates those declarations and derives the graph．`relations.parent: null` is reserved for the `ephy` ecosystem root．

## Current implementation state

The workspace bootstrap，status reporting，and ecosystem validation are implemented．Remote execution，physical-device orchestration，camera drivers，and the final Karte transport boundary remain design work in their owning repositories．No duration or completion percentage is inferred from these states．
