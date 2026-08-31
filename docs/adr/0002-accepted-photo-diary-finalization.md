# Karte automatically finalizes diaries from accepted photos

## Status

Accepted

## Context

The user wants Ephy to place the day's photos in a Karte diary without requiring a second diary-review action．At the same time，capture must not imply permanent retention or canonical Karte modification．The existing integration boundary sends generated content through staging or an outbox before canonical import．

## Decision

A photo becomes eligible for automatic diary finalization only after a separate，traceable acceptance decision changes it to `accepted`．Karte accepts a `DiaryCandidate` through its outbox，verifies that all referenced assets are accepted，imports the assets，validates the Markdown and metadata，and atomically promotes the entry to the canonical daily diary．The configured automatic-finalization policy is the user's prior authorization for that promotion，so no second review is required．

The diary operation is idempotent for one Ephy instance and local date．The configured instance timezone determines the date．A failed validation or import leaves the candidate in the outbox and does not partially modify canonical Markdown or accepted media．Capture permits，raw place evidence，and non-accepted media never enter the diary．Corrections and late acceptances update the same diary through an auditable operation．

The first implementation should use explicit user acceptance for the photo lifecycle．Policy-based photo acceptance may be added later only when the decision records the policy actor and revision．This ADR authorizes automatic diary finalization，not automatic photo acceptance．

## Consequences

- The user reviews or accepts a photo at most once; Karte does not require another confirmation for the daily entry．
- Captured but rejected or expired photos cannot leak into canonical memory．
- Karte needs transactional asset and Markdown import plus deterministic idempotency behavior．
- Late acceptance，correction，and deletion require update semantics rather than creating duplicate diaries．
- Ephy must preserve content hash，capture time，acceptance provenance，and trace identifiers across the outbox boundary．

## Alternatives considered

- Treat every capture as diary-eligible: rejected because capture is not consent to retain or record．
- Require manual review of both each photo and the completed diary: rejected because it duplicates approval after the asset is already accepted．
- Let the camera write directly into Karte content: rejected because the device cannot enforce canonical structure，transactions，or correction behavior．
- Generate a new diary file for every retry: rejected because retries and late photos would create duplicates．
- Embed images inside JSON or Markdown: rejected because binary media requires independent validation，storage，retention，and deletion．

## Related repositories

- `ephy-runtime`
- `ephy-cam`
- `karte`

## Date

2026-08-31

