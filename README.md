# Gate on Approach for Home Assistant

The driveway gate opens by itself as a family member drives home, timed so that it is
**open when the car gets there**: not still shut, and not already closing again.

It runs on Home Assistant with the companion app's GPS on each phone. Nobody presses
anything and nothing is mounted in the car.

## Why this is harder than a geofence

A plain "person enters zone, open gate" automation fails on a real driveway gate:

- **Phones report location every 40-120 s while driving.** A 400 m geofence is about
  22 s of travel at 40 mph, so the car can cross it between two samples. The open then
  fires late, with the car already waiting at a shut gate.
- **The gate auto-closes on a fixed cycle.** One pulse gives ~20 s to open, ~90 s held
  open and ~20 s to close. Pulse too early and the gate is closing again on arrival;
  pulse too late and the car waits. The usable window is roughly pulse + 20 s to
  pulse + 110 s.
- **One relay does open, close and stop.** A pulse while the gate is moving stops it
  dead, part-open. Every pulse therefore has to be guarded on "fully closed", which
  also means nothing can rescue a gate stopped mid-travel.
- **The contact sensor reads "closed" 3-7 s before the motor stops.** A pulse in that
  gap stops the gate instead of opening it.

## How it works

```
 8 km   High accuracy ON (phone reports every ~15 s instead of 1-2 min)
 2.5 km Approach automation starts watching this person's distance
 500 m  Pulse the gate (only if closed 15 s and nobody else is pulsing)
        Retry loop: if it auto-closes before they arrive, pulse again
 400 m  Zone backstop: opens it if nothing else did
 100 m  Arrived; stop the retry loop
 home   High accuracy OFF after 5 min at home
```

| Piece | What it does |
|---|---|
| `blueprints/automation/gate_approach_open.yaml` | The main automation. Triggers far out, holds until the open distance, pulses, and re-pulses if the gate closes before arrival. |
| `blueprints/automation/gate_high_accuracy_approach.yaml` | Turns the phone's high-accuracy GPS on near home and off once home, so dense samples cost only a few minutes of battery (Android). |
| `packages/gate_approach.yaml` | Everything else, as an example for one gate and two people: the zone, distance sensors, the template cover, the shared lock, away timers, the zone backstop, and the watchdogs. |

### The safety rules (do not remove these)

1. **Pulse only a gate that has read closed for 15 s.** A pulse mid-travel strands it
   part-open, and the 15 s covers the sensor reading closed before the motor stops.
2. **One shared lock.** Every automation that can pulse the gate holds
   `input_boolean.gate_action_in_progress` around its pulse, so two people arriving
   together cannot double-pulse.
3. **An unavailable sensor is not "closed".** The template cover goes unavailable with
   its sensor, so every "closed" guard fails safe.
4. **Fresh location only.** The retry loop pulses only on a location report made after
   the gate last moved. Otherwise a slow phone in a car that is already through can
   reopen the gate behind it.

### Watchdogs

- **Stuck open:** open longer than 5 min (a normal cycle is ~130 s). It re-alerts every
  15 min, up to 4 times. The push has a one-tap Mute button, and the mute clears itself
  at 4am.
- **Sensor:** the gate was pulsed but the sensor did not read open within 45 s, or the
  sensor has been unavailable for 15 min.
- **Phone location:** a phone has not reported for 45 min, so it cannot open the gate.

## Install

1. Copy `blueprints/automation/*.yaml` to `/config/blueprints/automation/`.
2. Turn on packages in `configuration.yaml`:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```
3. Copy `packages/gate_approach.yaml` to `/config/packages/`. Replace the example
   entity names listed at the top of the file with yours.
4. Add the house's coordinates to `secrets.yaml` as `gate_zone_latitude` and
   `gate_zone_longitude`.
5. Check the config (Developer Tools > YAML > Check configuration), then restart.
6. For each phone, set the companion app's battery use to **Unrestricted**. Without that,
   Android delays location reports.

## Calibrate

The distance sensors measure to the **zone centre (the house)**, not to the gate.

1. Drive in and note the distance reading while the car sits at the shut gate. On the
   original install the gate was ~124 m from the centre.
2. **Arrived distance** (default 100 m) must be below that reading, so the loop keeps
   re-pulsing while you wait. It must also be above the reading once you are through,
   so the loop stops.
3. **Open distance** is set by drive time. The last ~900-1200 m took 110-125 s on every
   recorded trip, and the gate starts closing ~90 s after the pulse, so anything above
   ~700 m opened too early. 500 m worked.

### One value for everyone

People who ride together each trigger their own automation, and the earliest pulse
wins. Give every person the same distances and timings, or one person's setting will
decide every shared trip.

## Tuning used on the original install

| Setting | Value | Blueprint default |
|---|---|---|
| Trigger distance | 2500 m | 1600 m |
| Open distance | 500 m | 550 m |
| Arrived distance | 100 m | 100 m |
| Approach timeout | 900 s | 900 s (was 360 s) |
| Retry interval | 20 s | 20 s |
| Maximum passes | 8 | 6 |
| Closed settle | 15 s | 15 s |
| High accuracy arm / re-arm / disarm | 8047 / 4000 / 9700 m | same |
| High accuracy update interval | 15 s | 15 s |

## When the gate did not open

See [docs/DEBUGGING.md](docs/DEBUGGING.md) for how to read a missed arrival from the
automation traces and history. [docs/HISTORY.md](docs/HISTORY.md) lists every real
miss so far and what changed because of it.

## Known gaps

- **The zone backstop does not retry.** If someone opens the gate by remote just before
  you reach the zone, the backstop sees it mid-cycle and skips. Nothing reopens it after
  it closes unless the approach automation is still running.
- **Manual pulses (remote, keypad, app) do not take the lock.** HA cannot stop them
  landing mid-travel, and the sensor watchdog does not check them.
- **iOS:** the high-accuracy commands only work on Android. iPhones still work with the
  approach automation, on whatever sampling iOS gives.

## License

[MIT](LICENSE). This moves a real gate: test it on yours while watching, and keep the
"closed" guards. It is provided as is, with no warranty.
