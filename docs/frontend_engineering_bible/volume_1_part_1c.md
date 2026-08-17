# Captain AI OS — Frontend Engineering Bible
## Frontend Volume 1 — Part 1C
### Design Tokens, Typography & Spacing System

* **Version:** 1.0.0
* **Status:** APPROVED SPECIFICATION

---

### Objective
Define the foundational design system used throughout Captain AI OS. This specification establishes consistent design tokens, typography, spacing, sizing, borders, shadows, and elevation rules that every frontend component must follow.

This document defines design standards only. It contains no implementation details or frontend code.

---

### Design Token Philosophy
Every visual value used throughout the interface must originate from a centralized design token system. Hardcoded visual values should never be used directly inside components. All future frontend elements must inherit their appearance from the approved design tokens.

The design token system must ensure: Consistency, Scalability, Maintainability, Theme support, and Easy future customization.

---

### Token Categories
The design system contains standardized tokens for:
* Colors & Gradients
* Typography (Fonts, Sizes, Weights, Line Heights, Letter Spacing)
* Spacing & Layout Padding
* Border Radius & Border Width
* Shadows & Elevation Levels
* Blur Levels & Opacity Levels
* Motion Timing & Easing
* Layer Order (Z-Index Hierarchy)

Each category must remain internally consistent across the application.

---

### Typography Philosophy & Hierarchy
Typography should communicate clarity before style. Text should always remain readable regardless of screen size. Decorative fonts must never be used for primary interface elements.

The interface defines 11 distinct typography levels:
1. **Display Titles**
2. **Page Titles**
3. **Section Titles**
4. **Card Titles**
5. **Body Text**
6. **Secondary Text**
7. **Labels**
8. **Buttons**
9. **Captions**
10. **Status Indicators**
11. **Code Text** (Monospace)

---

### Spacing & Layout Rhythm
Spacing creates rhythm, balance, and readability. Every component follows a unified spacing scale. Random or arbitrary pixel values are strictly prohibited. Whitespace is treated as an intentional design element.

---

### Border Radius, Shadow & Elevation System
* **Border Radius System:** Standardized scale across components; each component category remains internally consistent.
* **Shadow & Elevation:** Shadows communicate depth and elevation rather than decoration. Elevation is established through a combination of **Shadow + Blur + Transparency + Lighting**.
* **Blur & Opacity Standards:** Blur supports depth perception without reducing readability. Opacity indicates hierarchy (inactive vs active).

---

### Motion Tokens & Layer Standards
* **Motion Tokens:** All animations use predefined motion timing and easing values.
* **Layer Standards:** Every element belongs to a predefined layer stacking hierarchy to ensure predictable z-index stacking.
* **Theme Readiness:** Token architecture supports multi-theme switching without requiring component redesigns.

---

### Scope
This specification defines design token philosophy, typography standards, text hierarchy, spacing philosophy, border radius standards, shadow/elevation/blur/opacity standards, motion tokens, layer standards, and theme readiness. It does not define specific numerical code values or framework CSS.

---

### Deliverable
After approval, every frontend component and screen in Captain AI OS must follow this unified design token, typography, and spacing system.

---

### End of Frontend Volume 1 – Part 1C
