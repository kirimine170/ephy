# Repository map

## Source of truth

`workspace/repositories.json` contains only clone coordinates and workspace policy．Direct dependencies，integration peers，and runtime platforms remain in each repository's `.ephy/project.yaml` and are collected by `scripts/validate_ecosystem.py`．

| Canonical ID | GitHub repository | Local directory | Role | Visibility |
| --- | --- | --- | --- | --- |
| `ephy` | `kirimine170/ephy` | `ephy` | Ecosystem meta repository | public |
| `ephy-repository-template` | `kirimine170/ephy-repository-template` | `ephy-repository-template` | Shared repository scaffold | public |
| `ephy-runtime` | `kirimine170/ephy-runtime` | `ephy-runtime` | Local-first agent runtime | public |
| `ephy-worker` | `kirimine170/ephy-worker` | `ephy-worker` | Authorized remote job worker | public |
| `ephy-physical-ci` | `kirimine170/ephy-physical-ci` | `ephy-physical-ci` | Physical-device CI integration | public |
| `ephy-cam` | `kirimine170/ephy-cam` | `ephy-cam` | Camera ingestion boundary | public |
| `ephy-model` | `kirimine170/ephy-model` | `ephy-model` | Model training and evaluation recipes | private |
| `karte` | `kirimine170/Karte` | `karte` | Canonical Markdown data application | public |
| `karte-renderer` | `kirimine170/Karte_renderer` | `karte-renderer` | Document rendering integration | public |
| `ephy-private` | `kirimine170/ephy-private` | outside default workspace | Private instance definitions | private |
| `karte-docs` | `kirimine170/Karte_docs` | optional | Restricted Karte documentation | private |

No downstream list is maintained here．Consumers are derived by reversing direct declarations．
