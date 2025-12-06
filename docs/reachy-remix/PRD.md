# **Product Requirements Document (PRD)**

## **Reachy Remix – Scratch-Lite Motion Builder**

---

## **1. Product Overview**

**Reachy Remix** is a lightweight, fully self-contained web app that lets kids build simple animation sequences for Reachy using **tap-to-add action blocks**, similar to Scratch or Blockly but radically simplified. The app uses **Gradio**, requires **no additional dependencies**, **no external memory**, and runs entirely from a **single Python file** plus Reachy’s motion functions.

The goal:
**Make controlling Reachy feel like play — safe, intuitive, visually fun, and editable in seconds.**

---

## **2. Target Users**

### **Primary Users**

* Kids ages **5–12**
* Beginners learning robotics or programming concepts
* Users who benefit from simple visual interaction (no reading required)

### **Secondary Users**

* Educators in classrooms or summer camps
* Parents demonstrating Reachy at home
* Robotics clubs needing a quick intro tool

---

## **3. Goals & Success Metrics**

### **Goals**

1. Provide the simplest possible UI for controlling Reachy's movements.
2. Allow kids to build sequences of motions (“dance programs”) using large, friendly blocks.
3. Maintain minimal dependencies — **Gradio only** + standard library.
4. Ensure the application runs in any environment without installing extra services or memory layers.
5. Make the experience fun enough that kids want to keep adding and replaying sequences.

### **Success Metrics**

* Kids create & replay **at least 3 motion sequences** within 2 minutes.
* Session length **> 5 minutes** typical.
* Sequence-building error rate near 0 (no crashes, no invalid states).
* Educators report the tool is usable without training or documentation.

---

## **4. Feature Requirements**

### **4.1 Core Features (MVP)**

#### **A. Move Palette**

* A set of large, tappable buttons representing actions:

  * 👋 Wave
  * 🤖 Robot Pose
  * 💃 Spin
  * 🙆 Stretch
  * 🕺 Dab
  * ⏸ Pause (optional block)

**Requirements:**

* Buttons must include both emoji + readable label.
* Clicking a button appends the move to the sequence.
* No drag-and-drop (tap-to-add only for simplicity).

---

#### **B. Sequence Display**

* A single-line visual display showing the current program.
* Display format:
  `Your Dance: 👋 🤖 💃 🕺`
* Must update instantly after any change (add / undo / clear).
* **Visual feedback:** New moves bounce into view with subtle animation.
* **Empty state:** Show friendly prompt: "Tap moves above to build your dance! 🎵"

---

#### **C. Play Controls**

* **▶️ Play:** execute the sequence on Reachy
* **↩️ Undo:** remove the last step
* **🧹 Clear:** delete the whole sequence

**Behavior:**

* If sequence is empty, Play should return message:
  *"Add at least one move first 🙂"*
* Play executes actions with a small delay between them (0.3–0.7 seconds).
* Reachy must complete each move fully before performing the next.
* **State management:** Simple state machine (IDLE → PLAYING → IDLE) prevents spam-clicking Play.
* **Micro-feedback:** Reachy gives subtle acknowledgment (head nod, eye blink) when each move completes.

---

## **5. Non-Functional Requirements**

### **5.1 Simplicity**

* No installation of additional libraries beyond:

  * `gradio`
  * `time`
  * standard library
  * Reachy SDK

### **5.2 Visual Design**

* **Theme:** Gradio's `gr.themes.Soft()` with custom colors:
  * Primary: Playful violet/purple
  * Secondary: Warm orange
  * Font: Kid-friendly (e.g., Fredoka, Poppins)
* **Button sizing:** Minimum 80x80px for easy tapping by small hands
* **Hover states:** Gentle scale-up (1.05x) on hover for responsive feel
* **Animations:** Emoji buttons should feel alive:
  * New moves bounce into sequence display
  * Sequence wiggles subtly when Play is pressed
* **Visual hierarchy:**
  * Move Palette: Bold, colorful (toy section)
  * Sequence Display: Subtle background, showcase area
  * Play Controls: Accent-colored action buttons

### **5.3 Performance**

* Sequence execution should start within < 150ms of pressing Play.
* UI must remain responsive while playing (no freezes).

### **5.4 Safety**

* All reachable motions must be **kid-safe**:

  * No fast whipping
  * No motions requiring high torque
  * No joint-limit extremes

### **5.5 Offline Capability**

* App must not require internet connection once running locally.

---

## **6. User Interaction Flow**

### **Step 1:** User opens the app

Gradio loads with:

* Move palette
* Empty sequence display
* Control buttons

### **Step 2:** User taps moves

Each tap updates the sequence visually.

### **Step 3:** User presses Play

Reachy performs each move in order.

### **Step 4:** User modifies sequence

Undo or Clear as desired.

### **Step 5:** User repeats until bored (preferably never)

---

## **7. Technical Requirements**

### **7.1 System Architecture (Simple & Extensible)**

* Single Python script with clean separation of concerns
* **Core engine pattern** (enables future expansion):
  ```python
  class MotionEngine:
      def execute(self, sequence: List[str]) -> None:
          """Pure motion logic - no UI coupling"""
  
  # Future extensibility:
  class VoiceEngine:  # Voice commands → motion sequence
      def parse(self, audio) -> List[str]: pass
  
  class VisionEngine:  # Gesture detection → motion sequence
      def detect(self, frame) -> List[str]: pass
  ```
* **UI Layer** (Gradio Blocks):
  * Left panel → Move Palette (colorful buttons)
  * Center → Sequence Display (showcase area)
  * Right panel → Play Controls (action buttons)
  * Bottom → Status messages
* **Separation principle:** Engines communicate through simple event/command pattern. New input modes (voice/vision) slot in without refactoring core logic.

### **7.2 Internal State**

* Sequence stored in `gr.State` as `List[str]`.

### **7.3 Move Execution**

`perform_move(move_id)` must map to actual Reachy SDK calls.

Example:

```python
if move_id == "wave":
    reachy.wave()
elif move_id == "dab":
    reachy.dab_pose()
```

**State Management:**
```python
class PlayState(Enum):
    IDLE = "idle"
    PLAYING = "playing"
    ERROR = "error"
```

### **7.4 Gradio Theme Configuration**

```python
theme = gr.themes.Soft(
    primary_hue="violet",
    secondary_hue="orange",
    font=gr.themes.GoogleFont("Fredoka"),  # Kid-friendly
    radius_size=gr.themes.sizes.radius_lg,  # Rounded buttons
)

# Custom CSS for animations
custom_css = """
.move-button:hover {
    transform: scale(1.05);
    transition: transform 0.2s ease;
}
.sequence-display {
    background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
    padding: 20px;
    border-radius: 15px;
}
"""
```

### **7.5 No Persistence (By Design)**

* No database
* No local JSON files
* No session storage
* No user accounts

**Philosophy:** Every session is a fresh canvas. This isn't a limitation—it's a feature that removes save/load complexity entirely. Each time you open the app, you start a NEW creation!

---

## **8. Future Enhancements (Not MVP)**

These are **optional**, not required for the first release:

### **8.1 Immediate Enhancements** (Same architecture)
* **Speed slider**
* **Random dance generator**
* **Sound effects** when building/programming
* **Achievement milestones** ("You made Reachy dance for 10 seconds!", "You used all 6 moves!")
* **Presets** (3–5 stored sequences within session memory)
* **Move editor** for educators
* **Multiple lanes** for multi-append behavior

### **8.2 Expansion via New Engines** (Clean architecture enables this)
* **Voice Engine:** "Reachy, add a wave!" → translates to button press equivalent
  * Input: Speech → Output: motion sequence
  * Same UI, different input method
* **Vision Engine:** Reachy watches user dance, copies moves
  * Input: Camera frames → Output: motion sequence  
  * Gesture detection maps to existing move palette
* **Multi-modal:** Combine voice + vision + touch seamlessly
  * All engines feed the same motion queue
  * Core gameplay loop remains pure

**Key principle:** New features are INPUT channels. The motion sequencer core stays stable.

---

## **9. Out of Scope**

* Drag-and-drop block editor (Blockly/Scratch embedded)
* Web Serial
* Cloud saving
* User accounts
* Complex programming structures (loops, conditionals)
* Installing third-party libraries besides Gradio

---

## **10. Acceptance Criteria**

### **10.1 Functional Requirements**
* The app launches with **no errors** in a clean Python environment.
* All move buttons append correctly to the sequence with visual feedback.
* Undo and Clear work 100% reliably.
* Play action performs the full sequence on Reachy without stalling.
* State machine prevents spam-clicking Play button.
* The app never produces unhandled exceptions during normal kid usage.
* All required features fit in a **single-file deployment** (+ Reachy SDK).

### **10.2 UX Requirements**
* Buttons are minimum 80x80px and easily tappable by kids.
* Theme is playful and colorful (violet/orange palette).
* New moves bounce into sequence display with animation.
* Empty state shows friendly prompt to get started.
* Hover states provide visual feedback on all interactive elements.
* Status messages are clear and encouraging (no technical jargon).

### **10.3 Architecture Requirements**
* MotionEngine class is decoupled from UI layer.
* Engine pattern allows future voice/vision integration without core refactor.
* Code structure supports adding new input modes as sibling engines.

---