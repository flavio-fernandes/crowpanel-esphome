# Historical material

These are pre-migration plans, handoffs, tool snapshots and physical observations,
not instructions for operating the current bench. Their original repository-relative
paths and commands are preserved as evidence and may no longer resolve from here.
Use [the current bench guide](../esphome-bench-cheatsheet.md).

In particular, the old flash-id-after-monitor-close recovery addressed a retired
network serial transport that could wedge the CrowPanel. The new independent
serial owner does not reset when a reader closes; do not repeat that workaround.

No old hardware PASS result here establishes that the CrowPanel has been installed
or tested on the new bench. Firmware, original README photos and HA configuration
were not changed by the client migration.
