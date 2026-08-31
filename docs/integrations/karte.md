# Karte integration boundary

## Current state

`ephy-runtime/packages/karte_core` currently imports and exports a simple JSON bundle and can render that representation as Markdown．This is a compatibility adapter prototype．It is not a completed integration with Karte's `content/` tree or `KARTE_DATA_DIR`．

## Phase 1 boundary

- Karte Markdown remains the canonical source．
- Ephy treats `KARTE_DATA_DIR/content` as a read-only source．
- Ephy output goes to a staging or outbox area and never overwrites canonical content directly．
- A user reviews output before Karte imports it by default．An accepted-photo daily diary may be promoted automatically under [ADR-0002](../adr/0002-accepted-photo-diary-finalization.md) because photo acceptance and the configured finalization policy provide prior authorization．
- The interchange preserves source path，project，tags，and updated time．
- Tests use synthetic fixtures，never actual Karte data．
- The existing JSON bundle adapter remains as a compatibility layer．

## Undecided transport

The formal boundary may use an API，file watcher，or IPC．That choice is not yet accepted and requires an ADR shared by the directly affected repositories．This setup does not connect to actual Karte data and performs no automatic writes．The target accepted-photo flow remains outbox-first and transactional; it does not authorize the camera device or `ephy-runtime` to overwrite canonical Karte content directly．See [the camera context architecture](../camera-context.md)．
