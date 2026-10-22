# When the gate did not open

Work out the time of the miss first, then read these three things in order.

## 1. The approach automation's trace

Settings > Automations > **Gate - Open on <name>'s Approach** > three dots > **Traces**.
Pick the run just before the arrival.

| The trace shows | It means |
|---|---|
| No run near that time | The distance never crossed the trigger distance going in. Check step 2: the phone was probably not reporting. |
| Stopped at the conditions | The away timer was running (they had just left), or the person already read "home". |
| **Aborted** at "Hold until close enough" | The approach timeout ran out before the distance reached the open distance. Step 2 shows why: a stop on the way, or samples too far apart. |
| Finished, but no `cover.open_cover` step | Every pass found the gate not closed for 15 s, the lock taken, or no fresh location. See step 3 for who else moved the gate. |
| Finished with `cover.open_cover` | HA pulsed it. If the gate did not move, check the relay and the sensor watchdog. |

Then check **Gate - Open on Zone Enter (backstop)** the same way. If the step "cover is
closed" failed with state `open`, the gate was mid-cycle when they entered the zone.

## 2. The distance history

History > the person's **Gate Distance** sensor around the arrival.

- **Gaps of a minute or more** near home mean high accuracy did not engage. Check the
  high-accuracy automation's trace, and that the app's battery setting is Unrestricted.
- **The distance going back up** means a stop or a detour, and the timeout may have run
  out (2026-10-21).
- **A sample at the gate reading** (about 120 m on the original install) with no pulse
  before it means the open distance was skipped between samples.

## 3. The gate's logbook

Logbook > the gate cover around the arrival. An open that says **triggered by** an
automation came from HA. An open with nothing after it came from outside HA: a remote,
the keypad or the manufacturer's app. Those can leave the gate mid-cycle just as someone
arrives.

## Reading it all at once (advanced)

In a browser tab signed in to Home Assistant, open the developer console. The frontend
exposes the websocket API:

```js
const hass = document.querySelector('home-assistant').hass;
const id = hass.states['automation.gate_open_on_alex_s_approach'].attributes.id;
await hass.callWS({type: 'trace/list', domain: 'automation', item_id: id});
await hass.callWS({type: 'history/history_during_period',
  start_time: '2026-10-21T20:00:00Z', end_time: '2026-10-21T21:40:00Z',
  entity_ids: ['sensor.alex_gate_distance', 'cover.front_gate', 'person.alex'],
  minimal_response: true, no_attributes: true});
await hass.callWS({type: 'logbook/get_events',
  start_time: '2026-10-21T21:00:00Z', end_time: '2026-10-21T21:40:00Z',
  entity_ids: ['cover.front_gate', 'input_boolean.gate_action_in_progress']});
```

The API answers in **UTC**; the UI shows local time.
