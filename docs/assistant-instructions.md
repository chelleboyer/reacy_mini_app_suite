TITLE: Assistant Execution Contract for Reachy Mini App Suite

GOAL:
- Build a suite of independent Reachy Mini apps.
- Keep all custom application code isolated in my own src tree.
- Use Pollen Robotics Reachy Mini repos ONLY as reference/source material, NOT as runtime dependencies.
c
REPO LAYOUT (TARGET STATE):

  /
  ├─ .bmad-core/                # (optional) BMAD method agents/config, if present
  ├─ docs/
  │   ├─ pre-prd.reachy-app-suite.md   # PRE-PRD for this app suite
  │   ├─ prd.md                       # (later) full PRD for the suite
  │   ├─ architecture.md              # (later) architecture doc for the suite
  │   └─ notes/                       # ad-hoc notes, design spikes, etc.
  ├─ src/                      # <-- OUR APPLICATION CODE ONLY
  │   ├─ apps/
  │   │   ├─ karaoke-duet/     # app: Reachy Karaoke Duet
  │   │   ├─ reachy-sings/     # app: Reachy Sings (solo/duet)
  │   │   ├─ oobe-demo-menu/   # app: main OOBE demo menu / launcher
  │   │   └─ (future apps...)  # additional independent apps
  │   ├─ common/               # shared utilities across our apps
  │   │   ├─ core/             # logging, config, http, HF client, etc.
  │   │   └─ reachy/           # high-level wrappers around Reachy APIs
  │   └─ __init__.py (if needed)
  ├─ src-reference/            # <-- ALL POLLEN / REACHY MINI REPOS LIVE HERE
  │   ├─ reachy-mini-fw/       # e.g. git submodule or cloned repo
  │   ├─ reachy-mini-examples/
  │   └─ (any other reference repos)
  ├─ tests/
  │   ├─ apps/
  │   └─ common/
  ├─ scripts/                  # helper scripts (dev tooling, not app logic)
  ├─ requirements.txt / pyproject.toml
  └─ README.md

HARD RULES FOR THE ASSISTANT:

1. SOURCE BOUNDARIES
   - I MAY ONLY implement / modify application logic inside:
     - src/apps/**
     - src/common/**
     - tests/**
   - I MUST NOT modify anything under src-reference/** unless the user explicitly asks me to.
   - I MUST treat src-reference/** as READ-ONLY reference code.

2. USE OF POLLEN / REACHY MINI CODE
   - I CAN open and read files under src-reference/** to:
     - Learn APIs, patterns, and usage of Reachy Mini code.
     - Copy small, relevant snippets (e.g., how to init the robot, basic motion scripts).
   - When copying:
     - I SHOULD adapt/clean/refactor code into our style and directory structure.
     - I SHOULD avoid 1:1 dumping entire files unless absolutely necessary.
     - I SHOULD NOT directly import modules from src-reference at runtime in our app code.
       - i.e., no `from src_reference.reachy-mini-fw import ...` etc.
   - I SHOULD assume we might later detach from src-reference, so our code in src/ must be self-contained.
   - I MUST respect licensing: if I copy code verbatim beyond small idiomatic snippets, I SHOULD:
     - Preserve license headers where needed.
     - Flag to the user that a given file includes copied/derived work.

3. RUNTIME DEPENDENCY CONTRACT
   - All runtime imports in our apps MUST originate from:
     - Python stdlib
     - Dependencies declared in requirements.txt / pyproject.toml
     - Our own code under src/common/** and src/apps/**
   - I MUST NOT create runtime imports that depend on src-reference/**.
     - That directory is for human/assistant reference only.

4. DOCUMENTATION & PRE-PRD / PRD
   - I SHOULD maintain:
     - docs/pre-prd.reachy-app-suite.md as the living PRE-PRD (vision + structure).
     - Later, docs/prd.md as the formal PRD derived from PRE-PRD.
   - When designing new apps or major features, I SHOULD:
     - Update the PRE-PRD or PRD with:
       - App description
       - User goals
       - Technical constraints
       - Integration points (OOBE, HF, etc.)

5. MULTI-APP STRUCTURE UNDER src/
   - Each app MUST live in its own folder under src/apps/:
     - Example: src/apps/karaoke-duet/, src/apps/reachy-sings/, src/apps/oobe-demo-menu/
   - Each app SHOULD:
     - Be installable/launchable independently.
     - Have a clear entry point (e.g. main.py or __main__.py).
     - Use shared utilities from src/common/** where applicable.
   - Shared concerns (HF client, device config, robot control wrappers, logging) SHOULD go into src/common/ so apps don’t duplicate them.

6. IDE / BMAD WORKING STYLE (IF .bmad-core IS PRESENT)
   - For planning (PRD, architecture), I SHOULD use PM/Architect-style behavior.
   - For implementation:
     - I SHOULD behave like the Dev agent:
       - Read PRD / PRE-PRD / architecture before coding.
       - Implement features in small, testable increments.
       - Keep a simple change log / notes in docs/notes/ or in story files if we use BMAD stories.
   - I SHOULD not invent extra files or structure outside the agreed layout without calling it out to the user.

7. OOBE & HF REQUIREMENTS (CONTEXT REMINDERS)
   - All apps in src/apps/** are part of a unified Reachy Mini “experience suite” supporting:
     - OOBE demo menu and simple-first experiences.
     - Hugging Face–installed apps (for singing, karaoke, demos, etc.).
   - I SHOULD:
     - Design each app with non-technical users in mind.
     - Keep CM4 constraints in mind (lightweight, small dependencies).
     - Keep an eventual HF packaging story in mind for each app.

8. SAFETY / HARDWARE GUARDRAILS
   - When writing motion/control code:
     - I MUST consider safe joint limits and movement speed.
     - I MUST prefer small, smooth motions by default.
     - I MUST avoid aggressive or unbounded loops that could stress hardware.
   - If I copy any motion examples from src-reference/**, I SHOULD:
     - Verify they are safe.
     - Adjust speeds and ranges conservatively.

END OF CONTRACT
