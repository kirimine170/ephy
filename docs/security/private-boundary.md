# Private-instance boundary

## Workspace isolation

`ephy-private` is excluded from default workspace bootstrap and should be cloned only into a separately access-controlled location．It must not be distributed to remote workers，physical CI hosts，camera devices，or other general execution environments．

## Allowed responsibility

The repository may define a private instance Constitution，immutable identity，individual name，dialogue Profile，and instance-specific runtime Policy settings．Runtime Policy implementation code belongs in `ephy-runtime`，daily memory belongs in Karte，and LoRA training data belongs under the `ephy-model` responsibility boundary．

## Prohibited content

The repository is not a credential vault．Do not commit raw conversations，daily memory，Karte production data，credentials，secret keys，raw LoRA datasets，model weights，unnecessary personal data，or inferred personality and owner values．Synthetic examples must be visibly fictional and contain no production-derived values．

GitHub visibility must be confirmed as private before any real instance value is introduced．Repository visibility alone does not replace encryption，least privilege，or an approved secret manager．
