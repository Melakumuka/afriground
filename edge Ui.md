# Walkthrough: Station Gateway Edge UI

We have successfully built out the **Station Gateway Edge UI**, serving as the critical bridge between the AfriGround cloud and the physical ground station hardware.

## 🖥️ 1. Edge Operator Console (`apps/station-gateway/templates/`)

We completely rewrote the local web templates to use the AfriGround dark-mode design system. This UI is designed to run locally on the station LAN, ensuring operators have a robust interface even if cloud connectivity is degraded.

- **`base.html`**: A responsive, unified layout with real-time cloud-sync indicators.
- **`dashboard.html`**: The main overview panel featuring:
  - Live hardware health dials (ACU status, HDR Modem lock, time sync drift).
  - A wind speed monitor with visual safety thresholds (Green/Yellow/Red warnings for stowing).
  - An upcoming pass queue showing priority, TX requirements, and readiness state.
- **`pass_console.html`**: The dedicated screen for each pass, which enforces safety constraints.

## 🛑 2. The Readiness Gate (Safety Interlock)

The `pass_console.html` now requires the station engineer to explicitly check off 5 mandatory items before they can click **CONFIRM READY**:
1. MCS Profile Loaded
2. HDR Configured
3. ACU TLE Updated
4. RF Path Verified
5. Weather & Environment Safe

*We added client-side JavaScript to keep the "CONFIRM READY" button disabled until all safety checks are physically validated by the human operator.*

## 🚨 3. Local-First Emergency Abort

We implemented a true **"Emergency Abort"** sequence that prioritizes hardware safety over cloud state. 

- **UI Update**: Added a prominent red `[ EMERGENCY ABORT ]` button to the Pass Console.
- **Adapter Interface (`adapters/base_adapter.py`)**: Added `kill_tx()` and `emergency_stow()` abstract methods.
- **Routing Logic (`routes/operator.py`)**: The `/abort` endpoint immediately triggers local hardware commands (`stop_pass_recording()`, `kill_tx()`, `emergency_stow()`) **first**, independent of whether the AfriGround cloud is reachable. It then marks the job as `FAILED` locally and attempts a best-effort sync to the cloud.

## 📄 4. Post-Pass Execution Receipts

When a job reaches the `COMPLETED` state, the Pass Console now automatically polls the local hardware adapter to fetch the post-pass artifacts (`collect_pass_artifacts()`). The UI cleanly displays:
- Average $E_b/N_0$ SNR (Signal-to-Noise)
- Maximum tracking error
- Total data volume (MB) recorded
- Cryptographic hash of the receipt for billing integrity

## 📚 5. User Guide Expanded

Finally, we comprehensively updated the `AFRIGROUND_USER_GUIDE.md` to include a dedicated **Station Engineer** section, detailing how to access the console, perform daily readiness workflows, and use the emergency abort controls.
