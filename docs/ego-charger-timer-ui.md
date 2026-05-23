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
screen push button
external switch.ego_charger changes from Home Assistant
sensor.ego_charger_power updates from Home Assistant
Home Assistant API availability changes
boot / reconnect / resync events
```

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

  ego_charger_off_led_blink_minutes: "10"
  ego_charger_off_led_dim_after_minutes: "60"
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

## Screen Button Behavior

### OFF + Screen Blanked

A screen press wakes the screen only.

It should not start the charger on the first press if the screen was blanked.
This avoids surprise activation.

### OFF + Screen Visible

A screen press starts the charger timer.

```text
active_timer_end_time = now + preset_duration_minutes
input_boolean.ego_charger_timer_active = on
switch.ego_charger -> on
FSM -> ON once switch state confirms on, or pending ON while awaiting confirmation
```

If the preset duration is missing, invalid, or less than 1 minute, reset it to
`ego_charger_default_timer_minutes` before starting.

### ON or CHARGING

A screen press turns the charger off immediately.

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

### External Switch Turns OFF While ON or CHARGING

If Home Assistant reports `switch.ego_charger == off` while the timer is active:

```text
transition to OFF
set timer_active = false
preserve preset_duration_minutes
clear pending_off if set
```

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

## Home Assistant Unavailable Behavior

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

LEDs use red behavior.

```text
0 to off_led_blink_minutes:
  red blinking

off_led_blink_minutes to off_led_dim_after_minutes:
  red pulsing

after off_led_dim_after_minutes:
  dim red pulsing
```

Initial values:

```text
blink for first 10 minutes
pulse until 60 minutes
dim pulse after 60 minutes
```

Screen blanking does not disable the LEDs.

### ON

LEDs are solid green.

### CHARGING

LEDs use a rainbow animation.

The rainbow animation should be pleasant and not frantic. It should imply
active charging without becoming visually annoying.

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

The countdown arc range is 1 minute through `max_timer_minutes`, initially 180
minutes.

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

Any ring movement or screen press while blanked wakes the screen.

If the screen is blanked and the user presses the screen, only wake it. Do not
start the charger from the first press after blanking.

## Secrets and Sensitive Data

Follow normal ESPHome best practices.

Use `secrets.yaml` for Wi-Fi, API keys, OTA passwords, encryption keys, and any
other sensitive values needed for Home Assistant access.

Do not hard-code Wi-Fi credentials, API encryption keys, OTA passwords, tokens,
or other secrets in the committed YAML.

## Implementation Notes

This file is a design spec, not the final implementation.

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
- While `OFF`, pressing the visible screen starts the charger timer.
- While `OFF` with the screen blanked, the first press only wakes the screen.
- While `ON` or `CHARGING`, pressing the screen turns the charger off.
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
