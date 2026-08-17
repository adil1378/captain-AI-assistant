# Captain AI OS — Frontend Engineering Bible
## Frontend Volume 2 — Part 2E
### Captain Core Audio-Reactive Behaviour

* **Version:** 1.0.0
* **Status:** APPROVED SPECIFICATION

---

### Objective
Define how the Captain Core conceptually responds to sound and communication. This specification establishes the relationship between Captain's visual presence and audio interaction. It describes behavioral principles only, not audio processing algorithms, waveform rendering, or implementation details.

---

### Design Philosophy
Captain should never appear disconnected from conversation. When the user speaks or Captain responds, the Captain Core should naturally reflect the communication without becoming a music visualizer or decorative equalizer. The visual response reinforces the feeling that Captain is actively participating in the conversation.

---

### Communication Awareness (7 Communication Phases)
The Captain Core conceptually recognizes 7 distinct communication phases:
1. **User begins speaking:** Transition from Idle/Waiting to Listening with immediate visual attention.
2. **User is actively speaking:** Smooth audio-reactive pulse and communication layer feedback.
3. **User pauses:** Calm expectation posture, preserving visual focus without resetting.
4. **User finishes speaking:** Smooth transition to Understanding/Thinking phase.
5. **User response trigger (Captain begins responding):** Shift to cyan energy shell & speech activation.
6. **Captain is responding:** Synchronized conversational cadence & voice activity modulation.
7. **Captain finishes responding:** Natural transition to Waiting state, then returning towards Idle.

---

### Behavioral Principles
* **Listening Behaviour:** Reassures the user that input is received with attention, focus, and readiness; never frantic.
* **Response Behaviour:** Communicates confidence, clarity, and intelligence in a conversational style.
* **Silence Handling:** Silence is an intentional state; Captain remains calmly present rather than frozen.
* **Speech Continuity & Multi-Modal Unity:** Continuous transitions between listening, thinking, and responding; consistent communication identity regardless of input method.
* **Emotional Neutrality:** Professional, composed engagement; subtle, context-appropriate expression.
* **Accessibility:** Audio-reactive visuals are never the sole source of critical information; users with reduced motion or mute receive full state clarity through non-audio UI indicators.

---

### Scope
This specification defines audio-reactive philosophy, 7 communication phases, listening/response behavior, silence handling, context awareness, accessibility, and expansion strategy. It does not define waveform graphics, FFT frequency analysis, speech synthesis, or Web Audio API code.

---

### Deliverable
After approval, every audio-related visual behavior of the Captain Core must follow these behavioral principles.

---

### End of Frontend Volume 2 – Part 2E
