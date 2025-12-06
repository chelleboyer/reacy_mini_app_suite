# PRE-PRD: Reachy Mini App Suite (Multi-App Under One src/)

## 1. Vision

Create a suite of small, delightful, CM4-friendly Python apps for Reachy Mini that:
- Deliver a magical out-of-box experience (OOBE) for non-technical families.
- Are installed via Hugging Face (HF) as lightweight “apps”.
- Live together in a single repository and unified `src/` folder, but remain independent:
  - Each app has its own folder, entry point, and UX purpose.
  - Shared logic is centralized in `src/common/`.

The suite should make Reachy Mini feel:
- Playful and approachable.
- Easy to use without coding.
- Extensible by developers via Hugging Face.

---

## 2. High-Level Goals

1. **OOBE First**
   - Provide a main demo menu and a few highly polished apps that work “out of the box”.
   - Focus on non-technical users opening Reachy Mini during holidays.

2. **Multi-App Under One Codebase**
   - Support multiple independent apps under `src/apps/`, e.g.:
     - `oobe-demo-menu` – main launcher / demo hub.
     - `reachy-sings` – robot singing in various styles, powered by HF.
     - `karaoke-duet` – you + Reachy karaoke, lyrics on phone, optional robot vocals.
     - `duet-stage` – two-Reachy duet performances (Sonny & Cher vibe).
     - Future apps (games, teaching, exercises, etc.).

3. **Reference-Only Vendor Code**
   - Include Pollen Robotics / Reachy Mini repositories under `src-reference/`:
     - For reading, learning APIs, and optionally copying/adapting code.
     - Not used as runtime imports.
   - Our apps in `src/` must be self-contained.

4. **HF-Installable**
   - Design apps so they can be packaged and published via Hugging Face.
   - Eventually support:
     - HF-powered audio generation for singing.
     - HF-powered configuration or content fetch (e.g., song lists).

---

## 3. Non-Goals (for Now)

- Full on-device ML for singing or CV; heavy models stay off-device.
- Complex monolithic “super app” – we want small, focused apps.
- Deep integration with the Pollen repos as runtime packages (we keep them reference-only).
- Supporting every possible Reachy hardware configuration initially; we start with common CM4-based, typical Reachy Mini setup.

---

## 4. Repository & App Structure

### 4.1 Top-Level Layout (Target)

- `docs/`
  - `pre-prd.reachy-app-suite.md` (this file)
  - `prd.md` (future detailed PRD)
  - `architecture.md` (future technical design)
  - `notes/` (scratch / design notes)

- `src/` (our application code)
  - `apps/`
    - `oobe-demo-menu/`
      - Responsible for:
        - First-run experience
        - “Pick an app” UI
        - Launching other apps or endpoints
    - `reachy-sings/`
      - Robot singing solo or with another robot, in selectable styles.
      - Integrates with HF backend(s) to fetch audio + timing.
    - `karaoke-duet/`
      - User sings, Reachy sings or performs alongside.
      - Lyrics on phone, audio playback on Reachy.
    - `duet-stage/`
      - Two-Reachy duet choreography and performance.
    - `(future apps ...)`
  - `common/`
    - `core/` – logging, config, HTTP client, HF client, simple scheduler, etc.
    - `reachy/` – high-level wrappers around Reachy APIs (connect, move, safe limits, poses).
    - `ui/` – shared web UI helpers (templating, static file serving).

- `src-reference/`
  - `reachy-mini-fw/` – Pollen Robotics firmware / SDK repo(s)
  - `reachy-mini-examples/` – official example scripts and demos
  - (other relevant Pollen repos as needed)

- `tests/`
  - `apps/` – tests per app
  - `common/` – tests for shared utilities

---

## 5. App Design Principles (For Every App in src/apps/)

1. **Independence**
   - Each app must be runnable independently (via CLI or a web endpoint).
   - Clear entry point (e.g., `main.py`, `__main__.py`, or a documented launch function).

2. **Shared Utilities**
   - No app-specific copies of generic behavior (logging, HTTP, HF client, basic robot control).
   - Those go into `src/common/` and are imported from there.

3. **Non-Technical User Experience**
   - Minimal configuration required.
   - Simple web UI or single-button invocation.
   - Clear feedback (animations, lights, text).

4. **Safe Hardware Interaction**
   - Respect joint limits and recommended speeds.
   - Prefer small, smooth motions.
   - Fail-safe: if something goes wrong, stop motion and return to a neutral safe pose.

5. **HF Integration (Where Applicable)**
   - Offload heavy compute (singing generation, etc.) to Hugging Face.
   - CM4 side acts as:
     - A thin client to request content.
     - A player/animator for precomputed assets.

---

## 6. OOBE-Specific Requirements

The suite must support a polished OOBE flow:

1. After first boot (post-build), user can:
   - Connect to robot’s web UI.
   - See an OOBE landing page driven by `oobe-demo-menu`.

2. OOBE page:
   - Offers a handful of apps:
     - “Wave Hello”
     - “Dance”
     - “Reachy Sings”
     - “Karaoke Duet”
   - Explains each with one-line descriptions and big buttons.

3. All apps launched from OOBE:
   - Must “just work” with default configuration.
   - Must show something fun within seconds.

---

## 7. Dependencies & Constraints

- **Runtime Environment**
  - CM4 (Raspberry Pi Compute Module 4).
  - Linux-based OS (likely a Pi OS variant).
  - Python 3.x.

- **Constraints**
  - Avoid heavy frameworks and large ML weights on-device.
  - Minimal external dependencies; prefer stdlib + a few well-chosen libraries (e.g., FastAPI/Flask, simple audio playback libraries).

- **Reachy Code**
  - Pollen’s official repos used as reference only in `src-reference/`.
  - Our app code must remain portable and self-contained.

---

## 8. Future PRD / Architecture Work

This PRE-PRD will eventually be elaborated into:

- A full **PRD (`docs/prd.md`)**:
  - Detailed requirements per app.
  - Detailed OOBE flow.
  - HF integration specifics.
  - Test scenarios.

- An **Architecture Doc (`docs/architecture.md`)**:
  - Exact module layout under `src/common/`.
  - App boundaries and interfaces.
  - Communication patterns (e.g., web server, RPC, CLI).
  - HF communication protocols.
