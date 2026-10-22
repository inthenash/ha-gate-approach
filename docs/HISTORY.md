# History - every real miss and what it changed

Each rule in the blueprints exists because of a day on this list.

| Date | What happened | What changed |
|---|---|---|
| 2026-09-06 | A plain 400 m zone trigger fired 55 s late. The boundary was crossed between two location samples, so the car was already at a shut gate. The same phone was also sending cached network fixes every ~15 min and went silent for 116 s on the final approach. | `gate_approach_open` blueprint: trigger far out, hold until the open distance, use `wait_template` (not `wait_for_trigger`) so a jump straight past the threshold still counts. Phone location watchdog added. |
| 2026-09-07 | The gate shut 1 s before arrival, every time. The 1000 m threshold was measured to the house, and the gate is ~124 m short of it, so it was really 876 m of driving: 120 s against 115 s of open time. | Calibrate against the gate, not the zone centre. Arrived distance set to 100 m, just past the gate. |
| 2026-09-21 | The gate's contact sensor latched "on" (a rusted reed switch, replaced on 09-28). Every pulse waits for "closed", so nothing opened the gate for a day. | Sensor watchdog: alert when a pulse gets no "open" from the sensor within 45 s. |
| 2026-09-22 | During an integration reload, the cover read "closed" while its sensor was unavailable. Separately, a second gate's cover read "closed" for hours while it stood open. | Template cover `availability` follows the sensor, so an unknown gate is never "closed". |
| 2026-09-22 | With high accuracy off, an approach jumped 939 m to 131 m in one gap. | `gate_high_accuracy_approach` blueprint (dense GPS only near home). Open distance briefly raised to 1300 m. The watchdog's "turn high accuracy back on" nag was removed. |
| 2026-09-25 | High-accuracy commands reached a dozing phone 5-10 min late, after it was already home. | Commands sent with `priority: high`, `ttl: 0`. |
| 2026-09-30 | Two people in one car: the 1300 m instance pulsed at ~1150 m and the gate was closing as they reached it. | Open distance 500 m, the same for everyone. |
| 2026-09-30 | Two re-pulses fired 3 s after the sensor read "closed". One did nothing and one opened slowly: the motor was still running. | 15 s closed-settle before any pulse. |
| 2026-09-30 | A slow phone in a car that was already through showed "outside" after the gate closed behind it. | Fresh-location rule: pulse only on a report made after the gate last moved. |
| 2026-09-30 | The sensor watchdog's "silent for 60 min" check alarmed every idle hour. A healthy sensor reports nothing while nobody uses the gate. | Removed. Only "no response to a pulse" and "unavailable 15 min" remain. |
| 2026-10-12 | High accuracy stayed on 15 min after arriving home. | Settled-at-home time cut to 5 min. |
| 2026-10-21 | A driver triggered at 2354 m, went back out to ~2000 m for 2 min (a stop or detour), and the 360 s approach timeout gave up at ~700 m, about 30 s short of the open distance. A remote then opened the gate just before the 400 m zone. The backstop saw it mid-cycle and correctly skipped, and it closed as the car arrived. The phone was fine: it reported every ~20 s. | Approach timeout 360 s to 900 s, for everyone. |
