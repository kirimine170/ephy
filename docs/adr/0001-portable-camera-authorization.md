# Portable camera authorization uses place-and-time permits

## Status

Accepted

## Context

`ephy-cam` is intended to be carried between locations．The user permits automatic capture only inside places and time windows they have authorized．A portable device cannot safely treat power，network connectivity，SSID，or GPS alone as permission．The camera also must not receive the complete instance policy or retain a detailed location history．

## Decision

Automatic capture requires a valid，short-lived `CapturePermit` that represents a successful evaluation of both an authorized place and an authorized time window．The local runtime or policy service evaluates long-lived instance policy and issues only the minimum authority needed for one source，a bounded set of purposes，a bounded number of captures，and a short expiry．

The camera gateway fails closed when the permit，place evidence，time，clock，capture indicator，or revocation state is uncertain．Manual arming or authenticated local evidence may establish place presence．Wi-Fi SSID or GPS alone does not authorize automatic capture．Raw coordinates and continuous location history are excluded from media envelopes and Karte by default．A local disable or revocation takes precedence over any permit．

The exact place-evidence adapters，permit encoding，and target gateway host remain implementation decisions as long as they preserve this boundary．

## Consequences

- Portable use can preserve the same authorization rule across different networks and rooms．
- The camera device holds less sensitive policy and cannot continue indefinitely with stale permission．
- Offline automatic capture is unavailable until a separately accepted design provides equivalent authorization，secure storage，expiry，and purge behavior．
- Clock，indicator，and evidence failures reduce capture availability because safety takes priority over opportunistic capture．
- Runtime，camera，and hardware tests need shared fixtures for allow，deny，expiry，revocation，and uncertainty cases．

## Alternatives considered

- Always allow automatic capture while the device is powered: rejected because power does not express place or time consent．
- Prompt before every capture: rejected as the only mode because it does not satisfy the requested automatic behavior inside an authorized context．It remains available as an explicit capture path．
- Use a registered SSID as the complete place check: rejected because SSIDs are ambiguous and spoofable．
- Use GPS geofencing as the complete place check: rejected because indoor availability and accuracy are insufficient，and precise location retention creates unnecessary privacy risk．
- Store the complete place schedule on the camera: rejected because it widens exposure when a portable device is lost and complicates revocation．

## Related repositories

- `ephy-cam`
- `ephy-runtime`
- `ephy-physical-ci`
- `ephy-private`

## Date

2026-08-31

