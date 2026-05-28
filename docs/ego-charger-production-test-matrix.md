# CrowPanel EGO Charger Production Test Matrix

Last reviewed: 2026-05-28.

This file is both the reusable production test plan and the historical evidence
from a 2026-05-24 test execution. State values and timestamps in
"Notes/evidence" sections are evidence from that run, not current live state.

## Scope and Assumptions

This test plan covers production readiness for the CrowPanel EGO charger timer UI in `esphome/crowpanel.yaml`, measured against `docs/ego-charger-timer-ui.md`.

Assumptions:

- The device under test is the CrowPanel ESPHome device named `crowpanel`.
- The production charger switch is `switch.ego_charger`.
- Home Assistant helpers are durable state used by the panel after reboot/reconnect.
- Codex may inspect the repo, validate/compile ESPHome YAML, query Home Assistant, use existing ESPHome diagnostic/test entities, and optionally inspect logs/camera evidence.
- Codex must not flash firmware, change secrets, push to GitHub, or use destructive HA operations outside the normal charger state machine without explicit approval.
- Camera observation is optional supporting evidence only. If no camera is available, display/LED checks require local visual confirmation.
- During this execution, `/dev/v4l/by-id` was not present, so no local camera evidence was captured.

## Test Environment Prerequisites

- Repo checkout at `~/src/crowpanel-esphome` or another local path.
- ESPHome/devcontainer workflow available:
  - `devcontainer exec --workspace-folder . esphome config esphome/crowpanel.yaml`
  - `devcontainer exec --workspace-folder . esphome compile esphome/crowpanel.yaml`
- Home Assistant reachable through the configured `HA_URL` and `HA_TOKEN` workflow when HA tests are run.
- CrowPanel added to Home Assistant through the ESPHome integration.
- In the ESPHome integration device settings, Home Assistant must allow this device to perform Home Assistant actions.
- Test buttons and diagnostic sensors from `esphome/crowpanel.yaml` should be enabled/available in Home Assistant.
- If camera evidence is used, `tools/crowpanel-camera-capture` or another configured camera source should be available.

## Required Home Assistant Entities

Production entities:

- `switch.ego_charger`
- `sensor.ego_charger_power`
- `input_number.ego_charger_preset_duration_minutes`
- `input_datetime.ego_charger_timer_end_time`
- `input_boolean.ego_charger_timer_active`
- `input_boolean.ego_charger_panel_pending_off`

CrowPanel diagnostic/test entities expected from the ESPHome device:

- `sensor.crowpanel_ego_charger_effective_state`
- `sensor.crowpanel_ego_charger_action_result`
- `button.crowpanel_ego_charger_test_tap`
- `button.crowpanel_ego_charger_test_ring_clockwise`
- `button.crowpanel_ego_charger_test_ring_counterclockwise`
- Optional: `sensor.crowpanel_wifi_signal`, `sensor.crowpanel_wifi_strength_percent`, `sensor.crowpanel_ip_address`.

Entity IDs may vary if Home Assistant has renamed the ESPHome device. ESPHome defines these as `text_sensor` components, but this HA instance currently exposes them as `sensor.crowpanel_...`; search for entities containing `ego_charger` and `crowpanel` if they differ.

## Required ESPHome Debug and Log Commands

- YAML validation:
  - `devcontainer exec --workspace-folder . esphome config esphome/crowpanel.yaml`
- Compile:
  - `devcontainer exec --workspace-folder . esphome compile esphome/crowpanel.yaml`
- Serial monitor, when hardware/log path is available:
  - `devcontainer exec --workspace-folder . tools/espwb-monitor`
- Workbench validation, if needed:
  - `devcontainer exec --workspace-folder . tools/validate-workbench.sh`
- Optional camera capture:
  - `tools/crowpanel-camera-capture`

Important log patterns:

- `screen press decision: source=... effective_state=... action=... switch_seen=... switch_state=... start_pending=... stop_pending=... pending_off=...`
- `EGO charger primary press source=...`
- `HA action switch.turn_on accepted`
- `HA action switch.turn_off accepted`
- `EGO charger start timed out; attempting fail-safe switch.turn_off`
- `Home Assistant unavailable; EGO charger turn-off is pending`
- `confirmed ON`
- `confirmed OFF`
- `effective state -> ...`

## Recommended Debug Hooks

Existing hooks in `esphome/crowpanel.yaml`:

- `sensor.crowpanel_ego_charger_effective_state`: diagnostic effective state.
- `sensor.crowpanel_ego_charger_action_result`: diagnostic last action/result.
- `button.crowpanel_ego_charger_test_tap`: routes through the same primary press script as touch/button with source `test`.
- `button.crowpanel_ego_charger_test_ring_clockwise`: exercises the same ring-adjust script with positive delta.
- `button.crowpanel_ego_charger_test_ring_counterclockwise`: exercises the same ring-adjust script with negative delta.
- Logs include source, effective state, action, switch_seen, switch_state, timer_active, remaining time, and pending flags for primary press decisions.

Missing or optional debug hooks that would materially improve testing:

- `text_sensor` for last press source, diagnostic and disabled by default if supported.
- `text_sensor` for last press decision/action, diagnostic and disabled by default if supported.
- Diagnostic `binary_sensor` or `text_sensor` values for `start_pending`, `stop_pending`, and local `pending_off`.
- Diagnostic `sensor` for local remaining seconds and preset minutes.
- A debug-only package such as `esphome/packages/ego-charger-debug.yaml` or a debug overlay such as `esphome/crowpanel-debug.yaml` that adds these hooks without polluting production firmware.
- A test button named "EGO Charger Test Physical Button Equivalent" may be useful if it routes through the same normal script with source `button`; it must not bypass the state machine.

Do not add buttons that directly set switch/helper state outside the normal state machine. Do not expose secrets.

## Codex-Executable Tests

### C001 - YAML/spec consistency check

- Category: Static inspection
- Preconditions: `esphome/crowpanel.yaml` and `docs/ego-charger-timer-ui.md` are present.
- Steps:
  1. Inspect substitutions, imported HA entities, primary press routing, ring behavior, timer/pending-off logic, LEDs, and debug hooks.
  2. Compare against the design expectations.
- Expected result: YAML uses the specified HA entities, routes touch and physical button through the same primary decision script, avoids LVGL `enter_button`, keeps OFF display confirmation tied to switch OFF, keeps pending-off sticky while switch is ON, uses fail-safe start timeout, and uses infinite rotary callbacks.
- How to observe result: Repo inspection with `rg`/`sed`.
- Pass/fail status: PASS
- Notes/evidence/log snippets:
  - Command: `rg -n "ego_charger_(switch_entity|power_entity|preset_duration_entity|timer_end_time_entity|timer_active_entity|panel_pending_off_entity)|ego_charger_screen_press|screen press decision|switch.turn_on|switch.turn_off|ego_charger_check_start_timeout|pending_off|EGO Charger Test Tap|EGO Charger Effective State|EGO Charger Action Result" esphome/crowpanel.yaml`
  - Evidence: substitutions match all required HA entity IDs; touch target, GPIO knob button, and test tap all execute `ego_charger_screen_press`; `ego_charger_check_start_timeout` attempts fail-safe `switch.turn_off`; `ego_charger_retry_pending_off` only clears pending-off when `switch.ego_charger` confirms OFF.

### C002 - ESPHome validation

- Category: Build/validation
- Preconditions: Devcontainer and secrets exist locally.
- Steps:
  1. Run `devcontainer exec --workspace-folder . esphome config esphome/crowpanel.yaml`.
- Expected result: ESPHome config validation passes.
- How to observe result: Command exit code and validation output.
- Pass/fail status: PASS
- Notes/evidence/log snippets:
  - Command: `devcontainer exec --workspace-folder . esphome config esphome/crowpanel.yaml`
  - Result: `INFO Configuration is valid!`

### C003 - ESPHome compile

- Category: Build/validation
- Preconditions: C002 passes.
- Steps:
  1. Run `devcontainer exec --workspace-folder . esphome compile esphome/crowpanel.yaml`.
- Expected result: Compile completes and produces a fresh firmware image for this YAML.
- How to observe result: Command exit code and compile summary.
- Pass/fail status: PASS
- Notes/evidence/log snippets:
  - Command: `devcontainer exec --workspace-folder . esphome compile esphome/crowpanel.yaml`
  - Result: `SUCCESS Took 68.47 seconds`; `INFO Successfully compiled program.`

### C004 - Required HA entities reachable

- Category: Home Assistant API
- Preconditions: HA reachable with configured `HA_TOKEN`/`HA_URL`.
- Steps:
  1. Query HA states for the six production entities and CrowPanel diagnostic/test entities.
- Expected result: Required entities exist and return states; test buttons are present or documented missing.
- How to observe result: HA REST API state responses.
- Pass/fail status: PASS
- Notes/evidence/log snippets:
  - Command: HA REST `/api/states` query using configured `HA_URL`/`HA_TOKEN`.
  - Found: `switch.ego_charger=off`, `sensor.ego_charger_power=2.0`, `input_number.ego_charger_preset_duration_minutes=65.0` during first inventory, `input_datetime.ego_charger_timer_end_time=2026-05-24 18:26:50`, `input_boolean.ego_charger_timer_active=off`, `input_boolean.ego_charger_panel_pending_off=off`.
  - Found CrowPanel buttons: `button.crowpanel_ego_charger_test_tap`, `button.crowpanel_ego_charger_test_ring_clockwise`, `button.crowpanel_ego_charger_test_ring_counterclockwise`.
  - Diagnostic sensors are present as `sensor.crowpanel_ego_charger_effective_state=OFF` and `sensor.crowpanel_ego_charger_action_result=pending_off clear action sent`.

### C005 - HA action permission confirmation

- Category: Home Assistant integration
- Preconditions: HA reachable and CrowPanel ESPHome device is connected.
- Steps:
  1. Prefer non-destructive evidence: inspect recent action-result sensor/logs for accepted HA actions.
  2. If no evidence exists, use a normal state-machine test tap only when safe and observe whether `switch.turn_on` or `switch.turn_off` is accepted.
- Expected result: Action-result/log evidence confirms Home Assistant accepts actions from the CrowPanel device, or the test is blocked with exact confirmation steps.
- How to observe result: `sensor.crowpanel_ego_charger_action_result`, logs, and switch/helper state changes.
- Pass/fail status: PASS
- Notes/evidence/log snippets:
  - Command: HA `button.press` on `button.crowpanel_ego_charger_test_tap`, observed through states and serial monitor.
  - Evidence: logs showed `HA action switch.turn_on accepted for switch.ego_charger`, `HA action input_boolean.turn_on accepted for input_boolean.ego_charger_timer_active`, `HA action switch.turn_off accepted for switch.ego_charger`, and pending-off helper actions accepted.

### C006 - Debug sensors update

- Category: Home Assistant diagnostics
- Preconditions: Diagnostic text sensors exist and CrowPanel is online.
- Steps:
  1. Read `EGO Charger Effective State`.
  2. Trigger an existing safe test button if available.
  3. Re-read `EGO Charger Action Result`.
- Expected result: Effective state and action result are present and update after test input.
- How to observe result: HA REST API state responses.
- Pass/fail status: PASS
- Notes/evidence/log snippets:
  - Command: read `sensor.crowpanel_ego_charger_effective_state` and `sensor.crowpanel_ego_charger_action_result`, then press `button.crowpanel_ego_charger_test_tap`.
  - Evidence: before start `effective_state=OFF`, `action_result=pending_off clear action sent`; after start/stop cycle, action-result changed through timer/helper action results and final state returned to `OFF`.

### C007 - OFF to STARTING/ON via simulated tap

- Category: State machine
- Preconditions: `switch.ego_charger` is OFF, HA is connected, and using the normal `EGO Charger Test Tap` path is acceptable.
- Steps:
  1. Record switch/helper/debug states.
  2. Press `button.crowpanel_ego_charger_test_tap`.
  3. Observe effective state and switch/helper state until STARTING or ON path is visible.
- Expected result: Simulated tap routes through primary press decision, starts timer, sets appropriate helper state, and does not display OFF after start until switch confirms OFF later.
- How to observe result: HA states, action-result text sensor, and logs if available.
- Pass/fail status: PASS
- Notes/evidence/log snippets:
  - Command: HA `button.press` on `button.crowpanel_ego_charger_test_tap`.
  - Before: `switch.ego_charger=off`, `timer_active=off`, `pending_off=off`, `effective_state=OFF`.
  - After 5s: `switch.ego_charger=on`, `sensor.ego_charger_power=650.0`, `timer_active=on`, `pending_off=off`, `effective_state=ON`, `timer_end_time=2026-05-24 18:11:04`.
  - Log: `screen press decision: source=test ... switch_state=0 ... effective_state=OFF action=start`; then `switch.ego_charger confirmed ON`.

### C008 - ON to OFF_PENDING/stop via simulated tap

- Category: State machine
- Preconditions: `switch.ego_charger` is ON or test C007 successfully started it.
- Steps:
  1. Press `button.crowpanel_ego_charger_test_tap`.
  2. Observe effective state, pending-off helper, timer helper, and switch state until OFF confirmation.
- Expected result: Simulated tap routes through primary press decision, requests stop, keeps pending-off while switch remains ON, and only returns to OFF after switch confirms OFF.
- How to observe result: HA states, action-result text sensor, and logs if available.
- Pass/fail status: PASS
- Notes/evidence/log snippets:
  - Command: second HA `button.press` on `button.crowpanel_ego_charger_test_tap`.
  - During stop: log showed `effective state -> OFF_PENDING`, `input_boolean.turn_on accepted for input_boolean.ego_charger_panel_pending_off`, then `switch.turn_off accepted`.
  - Final after 5s: `switch.ego_charger=off`, `sensor.ego_charger_power=2.0`, `timer_active=off`, `pending_off=off`, `effective_state=OFF`.
  - Log confirms OFF was reached after imported switch state: `switch.ego_charger confirmed OFF`, then `effective state -> OFF`.

### C009 - Helper state persistence

- Category: Home Assistant helpers
- Preconditions: HA reachable.
- Steps:
  1. Read `timer_active`, `timer_end_time`, `pending_off`, and `preset_duration`.
  2. Exercise ring/test tap paths where safe.
  3. Confirm helper state changes or persistence match the state machine.
- Expected result: Helpers reflect current timer intent and survive as HA states. Pending-off is not cleared while switch is ON.
- How to observe result: HA REST API state responses.
- Pass/fail status: PASS
- Notes/evidence/log snippets:
  - Commands: HA state reads around test ring and test tap paths.
  - Ring while OFF: preset changed `10.0 -> 15.0 -> 10.0`; `switch.ego_charger` stayed `off`, `timer_active=off`, `pending_off=off`.
  - Start: `timer_active=on`, `timer_end_time` updated to `2026-05-24 18:11:04`, `pending_off=off`.
  - Stop: `pending_off` was set during OFF_PENDING in logs and cleared after `switch.ego_charger` confirmed OFF; final `timer_active=off`, `pending_off=off`.

### C010 - Primary press log coverage

- Category: Logging
- Preconditions: Serial monitor or ESPHome logs are available.
- Steps:
  1. Trigger touch/test/button press path.
  2. Capture decision log.
  3. Confirm it includes source, effective_state, action, switch_seen, switch_state, and pending flags.
- Expected result: Decision logs include all fields needed to audit state-machine behavior.
- How to observe result: `tools/espwb-monitor` or ESPHome log output.
- Pass/fail status: PASS
- Notes/evidence/log snippets:
  - Command: `devcontainer exec --workspace-folder . tools/espwb-monitor` while pressing `button.crowpanel_ego_charger_test_tap`.
  - Start log: `screen press decision: source=test fsm_state=0 start_pending=0 stop_pending=0 pending_off=0 timer_running=0 switch_seen=1 switch_state=0 timer_active_seen=1 timer_active_state=0 remaining=0 last_action=pending_off clear action sent effective_state=OFF action=start`.
  - Stop log: `screen press decision: source=test fsm_state=1 start_pending=0 stop_pending=0 pending_off=0 timer_running=1 switch_seen=1 switch_state=1 timer_active_seen=1 timer_active_state=1 remaining=595 last_action=timer end action sent effective_state=ON action=stop`.

### C011 - No LVGL enter_button for primary action

- Category: Static inspection
- Preconditions: `esphome/crowpanel.yaml` is present.
- Steps:
  1. Search for `enter_button`.
  2. Confirm primary action is invoked by LVGL touch target and GPIO button directly.
- Expected result: No `enter_button` is configured for the primary action.
- How to observe result: `rg -n "enter_button|knob_button|ego_touch_target|ego_charger_screen_press" esphome/crowpanel.yaml`.
- Pass/fail status: PASS
- Notes/evidence/log snippets:
  - Command: `rg -n "enter_button|ego_touch_target|knob_button|ego_charger_screen_press" esphome/crowpanel.yaml`
  - Evidence: no `enter_button` match; `ego_touch_target`, `knob_button`, and test tap route directly to `ego_charger_screen_press`.

### C012 - Rotary encoder infinite control/no saturation

- Category: Static inspection
- Preconditions: `esphome/crowpanel.yaml` is present.
- Steps:
  1. Inspect rotary encoder config.
  2. Confirm it uses `on_clockwise` and `on_anticlockwise`, not a finite value range/min/max behavior.
- Expected result: Knob rotation is handled by direction callbacks and cannot saturate as a finite sensor value.
- How to observe result: `rg -n "rotary_encoder|on_clockwise|on_anticlockwise|min_value|max_value" esphome/crowpanel.yaml`.
- Pass/fail status: PASS
- Notes/evidence/log snippets:
  - Command: `rg -n "platform: rotary_encoder|on_clockwise|on_anticlockwise|min_value|max_value|position:" esphome/crowpanel.yaml`
  - Evidence: rotary encoder uses `on_clockwise` and `on_anticlockwise`. The only `min_value`/`max_value` matches are LVGL timer arcs, not the rotary encoder.
  - Runtime evidence: HA test ring clockwise/counterclockwise changed preset while OFF without changing switch state.

## Manual/Physical Tests

### M001 - Light display tap starts from OFF

- Category: Physical touch
- Preconditions: Switch OFF, display awake, HA connected.
- Steps:
  1. Lightly tap the display.
  2. Observe state transition and HA switch/helper state.
- Expected result: Tap starts timer through the normal primary action path.
- How to observe result: Display, LEDs, HA states/logs.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Requires local touch/display confirmation.

### M002 - Physical click starts from OFF

- Category: Physical button
- Preconditions: Switch OFF, display awake, HA connected.
- Steps:
  1. Physically click the knob/display button.
  2. Observe state transition and HA switch/helper state.
- Expected result: Physical click starts timer through the same decision path as tap.
- How to observe result: Display, LEDs, HA states/logs.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Requires local physical click confirmation.

### M003 - Light display tap stops from ON

- Category: Physical touch
- Preconditions: Switch ON with active timer.
- Steps:
  1. Lightly tap the display.
  2. Observe OFF_PENDING/stop path until OFF confirmed.
- Expected result: Tap requests stop and does not show OFF before switch confirms OFF.
- How to observe result: Display, LEDs, HA states/logs.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Requires local touch/display confirmation.

### M004 - Physical click stops from ON

- Category: Physical button
- Preconditions: Switch ON with active timer.
- Steps:
  1. Physically click the knob/display button.
  2. Observe OFF_PENDING/stop path until OFF confirmed.
- Expected result: Physical click requests stop through the same decision path as tap.
- How to observe result: Display, LEDs, HA states/logs.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Requires local physical click confirmation.

### M005 - Tap while blanked wakes only

- Category: Screen blanking
- Preconditions: OFF screen has blanked.
- Steps:
  1. Lightly tap display once.
  2. Confirm it wakes only.
  3. Tap again and confirm second tap starts.
- Expected result: First tap wakes screen without starting charger.
- How to observe result: Display, HA switch state, logs.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Requires blanked display observation.

### M006 - Physical click while blanked wakes only

- Category: Screen blanking
- Preconditions: OFF screen has blanked.
- Steps:
  1. Physically click once.
  2. Confirm it wakes only.
  3. Click/tap again and confirm second action starts.
- Expected result: First physical click wakes screen without starting charger.
- How to observe result: Display, HA switch state, logs.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Requires physical click/display observation.

### M007 - Rotate knob while OFF changes preset only

- Category: Physical ring
- Preconditions: Switch OFF, timer inactive.
- Steps:
  1. Rotate knob both directions.
  2. Confirm displayed preset changes.
  3. Confirm charger switch remains OFF.
- Expected result: Ring changes preset only and never starts the charger while OFF.
- How to observe result: Display and HA switch/helper states.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Requires physical ring/display confirmation.

### M008 - Rotate knob while ON changes active countdown only

- Category: Physical ring
- Preconditions: Switch ON with active timer.
- Steps:
  1. Rotate knob both directions.
  2. Confirm active countdown changes.
  3. Confirm switch stays ON and action is not treated as a stop/start.
- Expected result: Ring adjusts active countdown only.
- How to observe result: Display, HA helpers, switch state.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Requires physical ring/display confirmation.

### M009 - LED colors/effects

- Category: Physical LEDs
- Preconditions: Device running current firmware.
- Steps:
  1. Observe OFF awake.
  2. Observe OFF blanked.
  3. Observe ON.
  4. Observe CHARGING with power above threshold.
- Expected result: OFF awake is solid red, OFF blanked is slow/dim red breathing, ON is green, CHARGING is rainbow.
- How to observe result: In-person LED observation or optional camera.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Requires visual confirmation.

### M010 - No accidental double action on hard press

- Category: Physical touch/button interaction
- Preconditions: Switch OFF or ON in a controlled test state.
- Steps:
  1. Press hard enough that the hardware may generate both touch and button events.
  2. Observe only one effective primary action.
- Expected result: Debounce/decision path prevents double start/stop.
- How to observe result: Logs and HA state transitions.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Requires physical press and logs.

### M011 - Timer expiry turns charger off

- Category: Timer expiry
- Preconditions: Active timer with short duration.
- Steps:
  1. Start a short timer.
  2. Wait for expiry.
  3. Observe stop request and OFF confirmation.
- Expected result: Expiry attempts `switch.turn_off`, sets/keeps pending-off until OFF confirmed, then clears timer/pending helpers.
- How to observe result: Display, LEDs, HA states/logs.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Manual timing/observation recommended.

### M012 - HA offline during active timer behaves safely

- Category: HA resilience
- Preconditions: Active timer.
- Steps:
  1. Disconnect HA/network path to the panel.
  2. Observe local display state.
  3. Reconnect HA.
- Expected result: Local active/pending state remains visible and does not collapse to misleading OFF.
- How to observe result: Display and reconnect logs/states.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Requires physically or administratively disconnecting HA/network.

### M013 - HA offline at timer expiry sets pending_off and retries on reconnect

- Category: HA resilience
- Preconditions: Active short timer.
- Steps:
  1. Disconnect HA before expiry.
  2. Let timer expire.
  3. Reconnect HA.
- Expected result: Panel marks local pending-off, retries off on reconnect, and clears pending-off only after switch confirms OFF.
- How to observe result: Display, LEDs, HA states/logs.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Requires HA disconnect/reconnect control.

### M014 - Start timeout fails safe and attempts OFF

- Category: Fail-safe
- Preconditions: Controlled way to prevent switch ON confirmation after start request.
- Steps:
  1. Trigger start while switch confirmation is blocked/unavailable.
  2. Wait past start timeout.
  3. Observe fail-safe OFF attempt and pending behavior.
- Expected result: Start timeout attempts `switch.turn_off`, records failure/timeout, and remains pending until OFF is confirmed.
- How to observe result: Display, HA states/logs.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Requires controlled HA/switch behavior.

### M015 - External HA switch ON starts/protects with local timer

- Category: External HA changes
- Preconditions: Switch OFF and panel online.
- Steps:
  1. Turn `switch.ego_charger` ON from HA outside the panel.
  2. Observe panel resync/protective timer behavior.
- Expected result: Panel shows ON/CHARGING depending on power and starts/protects with local timer if helper import is incomplete.
- How to observe result: Display, HA helpers/logs.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Requires deliberate external HA switch change.

### M016 - External HA switch OFF clears timer and pending state

- Category: External HA changes
- Preconditions: Switch ON with timer active or pending-off.
- Steps:
  1. Turn `switch.ego_charger` OFF from HA outside the panel.
  2. Observe panel and helper cleanup.
- Expected result: Panel clears timer/pending state and shows OFF only after switch confirms OFF.
- How to observe result: Display, HA helpers/logs.
- Pass/fail status: MANUAL
- Notes/evidence/log snippets: Requires deliberate external HA switch change.

## Production Readiness Checklist

- [x] ESPHome config validates.
- [x] ESPHome firmware compiles cleanly.
- [x] Required HA entities are present and reachable.
- [x] CrowPanel is allowed to perform HA actions.
- [x] Touch and physical click route through the same effective-state decision path by static inspection; physical equivalence still needs manual confirmation.
- [x] No LVGL `enter_button` is used for primary action.
- [ ] First tap/click while blanked wakes only.
- [x] OFF to start path works through simulated input; physical input still needs manual confirmation.
- [x] ON/CHARGING to stop path works through simulated input; physical input still needs manual confirmation.
- [x] OFF is not displayed before switch OFF confirmation in simulated stop/log evidence.
- [x] `pending_off` remains sticky while switch is ON in simulated stop/log evidence.
- [ ] Start timeout fails safe and attempts OFF.
- [ ] HA offline active/pending state remains visible locally.
- [ ] Timer expiry turns charger off or remains pending until it can.
- [x] Rotary encoder acts as an infinite directional control and does not saturate by static inspection and test ring evidence.
- [ ] LEDs match OFF/blanked/ON/CHARGING requirements.
- [ ] No accidental double action from combined touch/button physical press.
- [ ] Manual physical tests M001-M016 completed.
