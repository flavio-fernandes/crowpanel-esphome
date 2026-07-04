# EGO Charger Timer UI Design

## Goal

Build a CrowPanel ESPHome + LVGL interface that controls the Home Assistant
charger outlet `switch.ego_charger` through a simple timer-oriented UI.

The panel should make it obvious whether the charger outlet is off, merely on,
or actively charging. It should also show the live power draw from
`sensor.ego_charger_power` while the timer is active.

The design must be safe, intuitive, and resilient across device reboots, Home
Assistant restarts, and manual changes made outside the CrowPanel.

## Target Home Assistant Entities

Production and mock Home Assistant environments should expose the same entity
IDs so the CrowPanel YAML does not need to change when moving between them.

```yaml
switch_entity: switch.ego_charger
power_entity: sensor.ego_charger_power
```

The switch controls power to the charger outlet.

The power sensor reports current draw in watts.

## High-Level UX

The CrowPanel behaves like a physical charger timer.

- In `OFF`, the outlet is off. The screen uses an unmistakable red/off theme.
- In `ON`, the outlet is on, a countdown is active, but the charger is not
  drawing meaningful power.
- In `CHARGING`, the outlet is on, a countdown is active, and the charger is
  drawing meaningful power.

The user should never have to wonder whether rotating the ring while `OFF`
starts the charger. It does not. While `OFF`, ring movement adjusts only the
preset duration for the next run.

## Finite State Machine

### States

```text
OFF
  switch.ego_charger is off.
  No operational countdown is running.
  The preset duration may be non-zero because it is only the next-start value.

ON
  switch.ego_charger is on.
  The operational countdown is running.
  sensor.ego_charger_power is not high enough to qualify as charging.

CHARGING
  switch.ego_charger is on.
  The operational countdown is running.
  sensor.ego_charger_power indicates active charging using hysteresis.
```

### Inputs

```text
ring rotation
display tap
physical click
external switch.ego_charger changes from Home Assistant
sensor.ego_charger_power updates from Home Assistant
Home Assistant API availability changes
boot / reconnect / resync events
```

### Primary Action Inputs

The CrowPanel has two user inputs that invoke the same primary charger action.

- `Tap` means a light touch on the round display.
- `Physical click` means pressing harder on the screen/knob assembly until the
  built-in button clicks.

For the EGO charger UI, both inputs are equivalent:

```text
OFF -> start timer
ON / CHARGING -> stop timer
screen blanked -> wake only
STARTING / OFF_PENDING / SYNCING / HA_UNAVAILABLE / failed states -> follow the effective-state decision rules
```

The implementation must route both inputs through the same effective-state
decision path. A physical user action must not be processed twice, even if the
hardware generates both a touch event and a button event close together.

Do not rely on LVGL `enter_button` for this primary action. ESPHome LVGL
`enter_button` is intended for LVGL focus and navigation behavior; pressing the
encoder can click the currently focused LVGL object, which is harder to reason
about and can vary with focus state. For this UI, the GPIO button press should
explicitly invoke the same primary-action script as the display tap. Keep the
rotary encoder wired only for rotation input unless future rotary focus
navigation truly requires otherwise.

### Outputs

```text
CrowPanel screen
Home Assistant service requests for switch.ego_charger
CrowPanel 5 RGB LEDs
Home Assistant helper updates for persisted timer intent
```

## Timer Model

Use separate values for the next-start preset and the active timer.

```text
preset_duration_minutes
  User preference / starting value.
  Can be changed while OFF.
  Is not a running timer.

active_timer_end_time
  Absolute timestamp for the active countdown.
  Exists only while ON or CHARGING.

remaining_seconds
  Derived from active_timer_end_time - now.
  Must be zero while OFF.
```

The FSM should not persist its state directly. It should reconstruct state from
Home Assistant entities and helpers.

### Invariants

```text
OFF:
  switch.ego_charger == off
  timer_active == false
  remaining_seconds == 0

ON:
  switch.ego_charger == on
  timer_active == true
  active_timer_end_time > now
  charging hysteresis says not charging

CHARGING:
  switch.ego_charger == on
  timer_active == true
  active_timer_end_time > now
  charging hysteresis says charging
```

## Recommended Home Assistant Helpers

Use Home Assistant as the durable source of truth for values that should
survive CrowPanel power cycles.

```yaml
input_number.ego_charger_preset_duration_minutes:
  min: 1
  max: 180
  step: 1
  mode: box

input_datetime.ego_charger_timer_end_time:
  has_date: true
  has_time: true

input_boolean.ego_charger_timer_active:

input_boolean.ego_charger_panel_pending_off:
```

`input_boolean.ego_charger_panel_pending_off` records that the panel attempted
or still needs to turn off the charger after timer expiry, but Home Assistant or
the switch entity was unavailable when the request was needed.

## Configurable Parameters

Keep these parameters in a clearly marked CrowPanel / EGO charger section of
the ESPHome YAML. Do not create a separate device just for configuration.

Starting values:

```yaml
substitutions:
  ego_charger_switch_entity: switch.ego_charger
  ego_charger_power_entity: sensor.ego_charger_power

  ego_charger_default_timer_minutes: "10"
  ego_charger_max_timer_minutes: "180"

  ego_charger_charging_enter_threshold_watts: "20"
  ego_charger_charging_exit_threshold_watts: "15"
  ego_charger_charging_power_stable_seconds: "10"

  ego_charger_off_led_visible_brightness: "35%"
  ego_charger_off_led_blanked_pulse_min: "15"
  ego_charger_off_led_blanked_pulse_max: "35"
  ego_charger_off_led_blanked_pulse_period_ms: "5000"
  ego_charger_off_screen_blank_minutes: "60"
```

Use `secrets.yaml` for Wi-Fi, API keys, OTA passwords, encryption keys, and any
other sensitive values needed for Home Assistant access.

## Charging Detection

Charging is inferred from switch state and power draw.

Use hysteresis to prevent flapping near the threshold.

```text
Enter CHARGING:
  switch.ego_charger is on
  timer is active
  sensor.ego_charger_power > charging_enter_threshold_watts
  condition remains true for charging_power_stable_seconds

Exit CHARGING:
  switch.ego_charger is on
  timer is active
  sensor.ego_charger_power < charging_exit_threshold_watts
  condition remains true for charging_power_stable_seconds
```

The stable timer should begin as soon as `sensor.ego_charger_power` publishes a
new value. In ESPHome, force the charging detector to re-evaluate from the power
sensor callback instead of waiting for a generic polling interval. This keeps
the hysteresis rule intact while making LEDs and the FSM feel responsive.

Initial values:

```text
enter threshold: 20 W
exit threshold: 15 W
stable duration: 10 seconds
```

If the power sensor is unavailable, do not enter `CHARGING`. Stay in `ON` and
show the power value as:

```text
-- W
```

## Ring Behavior

The ring adjusts timer values. It never directly toggles the charger.

### Adjustment Step Rules

```text
1 through 10 minutes:
  1-minute increments

Above 10 minutes:
  5-minute increments

Minimum:
  1 minute

Maximum:
  max_timer_minutes, initially 180 minutes
```

The decrement boundary should be intuitive:

```text
180 -> 175 -> ... -> 15 -> 10 -> 9 -> 8 -> ... -> 1
```

The increment boundary should be similarly intuitive:

```text
1 -> 2 -> ... -> 9 -> 10 -> 15 -> 20 -> ... -> 180
```

### Ring While OFF

Ring movement while `OFF` adjusts only `preset_duration_minutes`.

It must not turn the charger on.

The screen should wake if blanked, show the `OFF` layout, and make the meaning
obvious:

```text
OFF
Ready for 10 min
Rotate to adjust
Press screen to start
```

If the user tries to go below 1 minute, keep the value at 1 minute and show
brief feedback:

```text
Minimum preset is 1 min
```

If the user tries to go above the maximum, keep the value at the maximum and
show brief feedback:

```text
Maximum is 180 min
```

Use a small animation or haptic-like visual nudge to show that the boundary was
hit.

### Ring While ON or CHARGING

Ring movement while `ON` or `CHARGING` adjusts the active countdown.

- Clockwise rotation extends the active timer.
- Counter-clockwise rotation reduces the active timer.
- The same 1-minute / 5-minute step rules apply.
- The remaining time must never go below 1 minute due to ring movement.
- The remaining time must never exceed the configured maximum.

If the user tries to go below 1 minute while active, keep the remaining time at
1 minute and show brief feedback:

```text
Minimum is 1 min
Press screen to turn off
```

If the user tries to go above the maximum, keep the remaining time at the
maximum and show brief feedback:

```text
Maximum is 180 min
```

## Primary Action Behavior

### OFF + Screen Blanked

A tap or physical click wakes the screen only.

It should not start the charger on the first press if the screen was blanked.
This avoids surprise activation.

### OFF + Screen Visible

A tap or physical click starts the charger timer.

```text
active_timer_end_time = now + preset_duration_minutes
input_boolean.ego_charger_timer_active = on
switch.ego_charger -> on
FSM -> ON once switch state confirms on, or pending ON while awaiting confirmation
```

On the CrowPanel implementation, the tap action should be wired through an LVGL
click target that covers the round display. The physical click should be wired
from `knob_button.on_press` directly to the same common primary-action script.
Both paths should set a source marker such as `touch`, `button`, or `test`
before entering the common decision path so logs can show which input arrived.
The raw touchscreen callback may still log coordinates for diagnostics, but it
should not also run the start/stop action. This avoids missed clicks when LVGL
owns the input device and avoids double-processing one physical action.

The ESPHome implementation should command Home Assistant with explicit
`switch.turn_on` / `switch.turn_off` service calls for `switch.ego_charger`.
The imported Home Assistant switch state is the confirmation and resync source;
it should not be the only command path. This avoids a panel tap appearing to do
nothing when the local mirrored switch object does not forward control as the
user expects.

Home Assistant must explicitly trust/allow the CrowPanel ESPHome device to make
Home Assistant service/action calls. In the ESPHome integration device settings,
enable the option that permits Home Assistant actions/service calls from the
DUT. Without that trust setting, screen taps may run locally on the panel but HA
will reject or ignore the `switch.turn_on` / `switch.turn_off` request for
`switch.ego_charger`.

If the preset duration is missing, invalid, or less than 1 minute, reset it to
`ego_charger_default_timer_minutes` before starting.

### ON or CHARGING

A tap or physical click turns the charger off immediately.

```text
switch.ego_charger -> off
input_boolean.ego_charger_timer_active = off
clear or ignore active_timer_end_time
preserve preset_duration_minutes
FSM -> OFF once switch state confirms off
```

## Timer Expiry Behavior

When the active timer expires, turn off the charger regardless of whether the
state is `ON` or `CHARGING`.

```text
Timer expires:
  send switch.turn_off for switch.ego_charger
  set input_boolean.ego_charger_timer_active = off
  clear or ignore active_timer_end_time
  keep preset_duration_minutes unchanged
  transition to OFF once switch state confirms off
```

If Home Assistant is unavailable at expiry time:

```text
set input_boolean.ego_charger_panel_pending_off = on if possible
remember pending_off locally
send switch.turn_off as soon as Home Assistant reconnects
```

The charger must not be left on forever simply because the panel rebooted or
Home Assistant was temporarily unavailable.

## External Home Assistant Changes

The CrowPanel is not the only possible controller. The FSM must respond cleanly
to changes made from Home Assistant dashboards, automations, voice assistants,
or other clients.

### External Switch Turns ON While OFF

If Home Assistant reports `switch.ego_charger == on` while the panel believes it
is `OFF`, transition to `ON` and start a protective timer.

```text
if a valid future active_timer_end_time exists:
  use it
else:
  active_timer_end_time = now + preset_duration_minutes
  if preset_duration_minutes is invalid, use default_timer_minutes
  timer_active = true
```

This prevents the charger from being left on indefinitely after a manual or
external activation.

When `switch.ego_charger` confirms `on` after a panel-initiated start, start the
local protective timer immediately from the current preset. Do not wait for all
Home Assistant helper entities to arrive before the countdown begins.

If `switch.ego_charger` is `on` and the helper import is still incomplete after
15 to 30 seconds, start a protective local timer using the current preset or
`ego_charger_default_timer_minutes`.

### External Switch Turns OFF While ON or CHARGING

If Home Assistant reports `switch.ego_charger == off` while the timer is active:

```text
transition to OFF
set timer_active = false
preserve preset_duration_minutes
clear pending_off if set
```

`pending_off` is sticky while `switch.ego_charger` is `on`. Do not overwrite a
local `pending_off = true` with a stale Home Assistant helper value of `false`.
Only clear `pending_off` when `switch.ego_charger` confirms `off`.

### Command Echoes

When the CrowPanel sends a switch command, Home Assistant will echo the updated
switch state back to ESPHome. Treat that echo as confirmation of the requested
transition, not as a new external user action.

## Boot, Reboot, and Recovery Behavior

On boot or Home Assistant reconnect, the CrowPanel should resync before trusting
local assumptions.

### Boot With Switch OFF

```text
state = OFF
remaining_seconds = 0
timer_active = false
```

The preset duration should be loaded from the HA helper. If unavailable or
invalid, use the default.

### Boot With Switch ON and Valid Future Timer

```text
state = ON or CHARGING depending on power hysteresis
active_timer_end_time = persisted HA helper value
remaining_seconds = active_timer_end_time - now
```

### Boot With Switch ON and No Valid Timer

Start a protective timer.

```text
active_timer_end_time = now + preset_duration_minutes
if preset_duration_minutes is invalid, use default_timer_minutes
timer_active = true
state = ON or CHARGING depending on power hysteresis
```

### Boot With Expired Timer

If the persisted timer is active but already expired:

```text
send switch.turn_off
set timer_active = false
set or keep pending_off until switch confirms off
state = OFF once switch confirms off
```

### Home Assistant Reconnect With Unchanged State

A Home Assistant restart or a brief API disconnect usually reconnects with the
switch in the same state it had before. The implementation must not depend on
edge-triggered state callbacks to leave `SYNCING`, because ESPHome deduplicates
switch and binary sensor publishes: a reconnect that re-imports an unchanged
state fires no `on_turn_on` / `on_turn_off` edge.

```text
on reconnect:
  keep the last imported switch and helper state as the working estimate
  resync from a state import path that fires on every push, even when the
    value is unchanged (for example a text-sensor import of the switch state)
  never require a physical switch toggle to leave SYNCING
```

If the panel was showing an active countdown when the connection dropped, the
reconnect must return it to `ON` / `CHARGING` (or reconcile to `OFF`) without
user interaction.

### Home Assistant Side Failsafes

The panel cannot protect the charger while the panel itself is offline,
rebooting, or dead. The Home Assistant package should carry failsafe
automations built on the existing helpers:

```text
switch confirms off -> clear timer_active and panel_pending_off
panel_pending_off on while switch on -> switch.turn_off
timer_active on and end time passed (plus grace) while switch on -> switch.turn_off
switch on for max_timer_minutes with timer_active off -> switch.turn_off
```

Together with the panel FSM these guarantee the charger is never left on
indefinitely no matter which side restarts or disappears.

## Home Assistant Unavailable Behavior

The panel must not self-reboot merely because Home Assistant is unreachable.
Disable the ESPHome API `reboot_timeout` (`reboot_timeout: 0s`); the default
15-minute timeout would restart the panel during a long HA outage and destroy
the local countdown state this section depends on. Keep the Wi-Fi
`reboot_timeout` at its default so a genuinely wedged network stack still
recovers.

### HA Unavailable While OFF

The local UI should remain usable for preset adjustment.

- Ring can wake the screen.
- Ring can adjust the local preset display.
- The panel should not pretend the value was persisted until HA confirms it.
- Starting the charger should be blocked if switch control is unavailable.

Show feedback:

```text
Home Assistant unavailable
Cannot start charger
```

### HA Unavailable While ON or CHARGING

Keep the local countdown running.

If Home Assistant becomes unavailable while the charger is locally known to be
on or the timer is running, keep showing the local active or pending state with
a warning instead of replacing the active screen with a generic offline state.

If the user taps or physically clicks while Home Assistant is unavailable and
the charger is locally known to be on, set local `pending_off = true` and show
`OFF_PENDING`. The panel should retry the actual `switch.turn_off` action when
Home Assistant reconnects.

If the timer expires while HA is unavailable:

```text
remember pending_off locally
send switch.turn_off as soon as HA reconnects
```

Show a subtle warning on the active screen, but do not obscure the countdown.

## RGB LED Behavior

The CrowPanel has 5 RGB LEDs. They reinforce the FSM state independently of
screen blanking.

### OFF

LEDs use red-only behavior.

```text
OFF with screen visible:
  solid red at off_led_visible_brightness

OFF with screen blanked:
  red breathing/pulsing from 15% to 80% red intensity once per second
```

Initial values:

```text
visible OFF brightness: 35%
blanked OFF pulse: 15% -> 35% -> 15% every 5 seconds
```

Screen blanking does not disable the LEDs.
Once the OFF screen is blanked, the RGB LEDs should continue with a gentle
red-only breathing pulse so the device still communicates that the charger is
safely off without looking like an active charging animation or lighting the
display.

### ON

LEDs are solid green.

### CHARGING

LEDs use a rainbow animation.

The rainbow animation should be pleasant and not frantic. It should imply
active charging without becoming visually annoying.

When leaving `CHARGING`, explicitly stop the active LED effect before applying
the `ON` or `OFF` LED color. Relying on a solid-color update to replace an
addressable effect can leave the rainbow running on some ESPHome light
implementations.

## Minimal Active Screen Layout

The first active LVGL screen should avoid placing status or action labels on top
of the countdown arc. The acceptable minimal active layout is:

```text
small state label near the top: ON or CHARGING
thin colored countdown arc centered in the screen
large remaining-time label centered inside the arc
power label below the remaining time
one short action label below the arc: Tap to stop
```

Do not reuse the two-line OFF hint block on active screens if it collides with
the arc. OFF can show both rotate and tap hints; ON and CHARGING should
prioritize countdown readability and use one compact action hint.

The active state label should be small enough that `CHARGING` fits comfortably
above the arc on the 240x240 round display. Use compact label typography for
this row; the timer and power values carry the visual weight. Leave visible
clearance between the label and the top of the arc; a label that barely fits in
the camera view is too large for the physical UI.

Text should use a small high-contrast palette rather than all-white labels.
Recommended roles:

```text
state label:
  OFF = warm amber
  ON = fresh green
  CHARGING = bright aqua
time label = near-white
power label = cool cyan
secondary hint = soft mint
primary tap action = amber when starting, soft rose when stopping
unavailable/error action = coral red
```

Keep the colors bright enough for the camera and physical display, but avoid
making every label equally loud. The timer remains the visual anchor; color is
there to clarify status and action.

## Display Design

Use LVGL for the UI.

The visual design should make `OFF` versus active states immediately obvious.

### OFF Screen

Use a visibly different OFF layout and color theme. A dim/deep red background
or red-tinted theme is preferred over a bright alarming red.

Core elements:

```text
large: OFF
medium: Ready for 10 min
small: Rotate to adjust
small: Press screen to start
```

The active countdown arc and power artifacts are hidden in `OFF`.

A subtle animation is allowed, such as:

- a soft pulse on the `OFF` text
- a small idle dial movement
- a gentle glow around the preset duration

The animation must not make the user think the charger is running.

After `off_screen_blank_minutes`, initially 60 minutes, blank the screen while
remaining in `OFF`. LED behavior continues.

### ON Screen

Use a non-red active theme.

Core elements:

```text
arc countdown graph
large centered remaining time
power draw from sensor.ego_charger_power
small state label: ON
optional small hint: Press to stop
```

The active countdown arc should represent percentage remaining for the current
timer session, not percentage of `max_timer_minutes`. For example, a fresh
10 minute timer should render as a mostly full arc even though
`max_timer_minutes` is 180. `max_timer_minutes` is the adjustment ceiling, not
the visual countdown range.

The arc should animate gently as the countdown moves toward zero.

The center value should show remaining time in a human-friendly way:

```text
9:42
1h 25m
```

Power should show:

```text
0 W
42 W
-- W
```

Use `-- W` when the power sensor is unavailable.

### CHARGING Screen

Use the same layout as `ON`, but with a charging accent and `CHARGING` label.

Core elements:

```text
arc countdown graph
large centered remaining time
power draw from sensor.ego_charger_power
small state label: CHARGING
optional subtle charging animation
```

The transition from `ON` to `CHARGING` should feel rewarding but not disruptive.
For example:

- brief accent glow
- small lightning icon if available
- slightly more energetic arc animation

Avoid large modal popups for normal charging transitions.

## Countdown Arc Tick Mapping

The UI should visually emphasize the first 10 minutes more precisely than the
longer range.

```text
1 through 10 minutes:
  single-minute ticks

above 10 minutes:
  grouped 5-minute units
```

The display should not become cluttered with too many tick labels. Favor clean
major ticks and a smooth arc over a dense clock-face appearance.

## Screen Blanking Rules

Screen blanking applies only to `OFF`.

```text
if state == OFF and no user interaction for off_screen_blank_minutes:
  blank screen
  keep LEDs active
```

Any ring movement, display tap, or physical click while blanked wakes the
screen.

If the screen is blanked and the user taps or physically clicks, only wake it.
Do not start the charger from the first primary action after blanking.

## Secrets and Sensitive Data

Follow normal ESPHome best practices.

Use `secrets.yaml` for Wi-Fi, API keys, OTA passwords, encryption keys, and any
other sensitive values needed for Home Assistant access.

Do not hard-code Wi-Fi credentials, API encryption keys, OTA passwords, tokens,
or other secrets in the committed YAML.

## Implementation Notes

This file is a design spec, not the final implementation.

Even the first minimal LVGL implementation should preserve the major OFF versus
active visual distinction. Do not show the active countdown arc or live power
readout on the OFF screen just because those widgets will be needed later for
ON and CHARGING. The simplest acceptable OFF screen is plain text: OFF, the
next-start preset, and the rotate/press hints.

Suggested implementation order:

1. Create the HA helper entities in the mock Home Assistant environment.
2. Add substitutions and globals for charger timer configuration.
3. Import the HA switch and power sensor into ESPHome.
4. Implement the internal timer model with preset and active end time.
5. Implement OFF / ON / CHARGING FSM transitions without LVGL polish.
6. Add button behavior.
7. Add ring adjustment behavior and boundary feedback.
8. Add RGB LED state behaviors.
9. Add the basic LVGL OFF screen.
10. Add the active countdown arc and power display.
11. Add charging hysteresis.
12. Add boot/reconnect recovery behavior.
13. Add screen blanking.
14. Polish animations and visual feedback.

Keep each step small and testable.

## Acceptance Criteria

The implementation is considered good enough when all of the following are true:

- While `OFF`, rotating the ring never turns on `switch.ego_charger`.
- While `OFF`, the display clearly says it is off and shows the next-start
  preset duration.
- While `OFF`, tapping the visible display or physically clicking starts the
  charger timer.
- While `OFF` with the screen blanked, the first tap or physical click only
  wakes the screen.
- While `ON` or `CHARGING`, tapping the display or physically clicking turns
  the charger off.
- While `ON` or `CHARGING`, rotating the ring adjusts the active countdown using
  the 1-minute / 5-minute step rules.
- The timer expiry always attempts to turn off `switch.ego_charger`.
- If Home Assistant is unavailable at timer expiry, the panel retries turn-off
  when Home Assistant reconnects.
- `CHARGING` is detected using power hysteresis, not a single noisy threshold.
- `sensor.ego_charger_power` unavailable is displayed as `-- W`.
- LED behavior matches the FSM state and continues even when the OFF screen is
  blanked.
- Rebooting the CrowPanel does not leave the charger on indefinitely.
- External Home Assistant switch changes are reconciled safely.
- Sensitive data is kept in `secrets.yaml`, not committed to the repo.
