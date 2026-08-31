# ephy

## Overview

Meta repository，architecture registry，and workspace tooling for the Ephy ecosystem

## Role in the Ephy ecosystem

This repository is an Ephy `meta` project．Its status is `active` and its intended visibility is `public`．Repository relationships are declared in `.ephy/project.yaml`．

## Goals

- Describe the outcomes this repository owns．
- Keep responsibilities aligned with its declared Ephy project type．

## Non-goals

- Do not duplicate responsibilities owned by related repositories．
- Do not maintain a downstream repository registry in this repository．

## Current status

The current implementation status is `active`．This label describes observed implementation state，not a delivery date or completion percentage．

## Architecture

This meta repository owns the workspace manifest，ecosystem validation，repository map，and shared architecture boundaries．It contains no runtime implementation，model weights，or private instance values．See [the ecosystem architecture overview](docs/architecture-overview.md) and record durable decisions under `docs/adr/`．

## Repository relationships

- Parent project: `None — ecosystem root`
- Direct dependencies:
  - None declared．
- Integration peers:
  - None declared．
- Runtime platforms:
  - None declared．

Declare only the parent and direct relationships．Do not list downstream consumers，and do not use Git submodules to represent ecosystem relationships．See [docs/repository-relations.md](docs/repository-relations.md)．

## Getting started

Open the non-Git parent directory containing this repository，then check or bootstrap the sibling repositories:

```bash
python3 ephy/scripts/bootstrap_workspace.py --dry-run
python3 ephy/scripts/workspace_status.py
python3 ephy/scripts/validate_ecosystem.py
```

Private repositories are never auto-cloned．Use `--include-private` only with explicit access and keep `ephy-private` outside the default workspace．

## Testing

Run the meta-repository and ecosystem checks with:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_repository.py
python3 scripts/validate_ecosystem.py
```

## Security and data handling

The data classification is `public`．Do not commit secrets，unnecessary personal data，raw conversation history，production Karte data，master camera images，raw LoRA training data，or model weights．See [docs/security-and-data.md](docs/security-and-data.md)．

## Documentation

- [Architecture](docs/architecture.md)
- [Ecosystem architecture overview](docs/architecture-overview.md)
- [Camera context architecture](docs/camera-context.md)
- [ephy-cam Codex implementation handoff](docs/implementation/codex-handoff.md)
- [Karte integration boundary](docs/integrations/karte.md)
- [Repository relationships](docs/repository-relations.md)
- [Security and data handling](docs/security-and-data.md)
- [Architecture Decision Records](docs/adr/README.md)

## License

No license has been selected automatically．Determine the repository's visibility and license explicitly before distribution，then add the appropriate license file and update this section．
