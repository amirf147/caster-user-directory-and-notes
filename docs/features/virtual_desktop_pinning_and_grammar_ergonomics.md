[ 🏠 Docs Home ](../README.md) › [ 📁 Features ](../README.md#features) › **Virtual Desktop Pinning Architecture, Phonetic Misrecognition & Grammar Ergonomics**

---

# Virtual Desktop Pinning: Architecture, Phonetic Misrecognition & Grammar Ergonomics

This document details the engineering, acoustic phonetic analysis, grammar design trade-offs, and upstream dependency coordination for virtual desktop window and application pinning in Caster. It analyzes the failure mode where the spoken command `pin window` misrecognizes as `new window`, evaluates the acoustic coarticulation mechanics in Kaldi speech models, assesses syntactic alignment within Caster grammar rules, and outlines upstream pull request strategies across Caster and PyVDA.

---

## 1. Executive Summary & Problem Scope

Virtual desktop pinning allows a user to keep specific windows or entire applications visible across all Windows virtual desktops. While Windows provides native GUI affordances (Task View context menus) for pinning, it lacks built-in keyboard shortcuts. Providing low-latency, deterministic voice commands for pinning removes the need to manually open Task View or navigate desktop grids.

During empirical validation of the initial Caster implementation, two distinct issues emerged:
1. **Phonetic Misrecognition:** The voice command `pin window` frequently misrecognized as `new window` in the Kaldi speech engine, triggering active browser or editor rules that spawned unintended windows.
2. **Sub-AUMID Multi-Window Pinning Failure:** In the underlying `pyvda` dependency, calling `pin_app()` on modern packaged applications (e.g., Windows Terminal) only pinned the isolated active window instance due to synthetic sub-AUMID generation (`~Wh~w<HEX_HWND>`) in the Windows Shell.

This document examines both problems, details their structural root causes, and outlines the production solutions.

---

## 2. Virtual Desktop Pinning Architecture in Caster

The virtual desktop pinning feature is implemented across three layers in Caster:

```
+-------------------------------------------------------------+
|        WindowManagementRule (castervoice/rules)             |
|   Grammar specs: ([toggle] pin | unpin) window / app        |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|         virtual_desktops.py (castervoice/lib)               |
|   Platform dispatch layer (win32 check and fallbacks)       |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|     windows_virtual_desktops.py (castervoice/lib)           |
|   HWND acquisition -> pyvda.AppView -> Caster HUD output    |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|           PyVDA COM Bridge (twinui.pcshell.dll)             |
|   IVirtualDesktopPinnedApps: PinView / PinAppID             |
+-------------------------------------------------------------+
```

### A. Component Breakdown

1. **`castervoice/rules/core/navigation_rules/window_mgmt_rule.py`**:
   Exposes the voice commands to the Dragonfly grammar engine. It maps spoken phrases to function calls in `virtual_desktops.py`.

2. **`castervoice/lib/virtual_desktops.py`**:
   Acts as the platform abstraction layer. On Windows (`sys.platform == "win32"`), it imports concrete pinning functions from `windows_virtual_desktops.py`. On unsupported platforms, it defines fallback stubs that report status via `printer.out`.

3. **`castervoice/lib/windows_virtual_desktops.py`**:
   Implements native Win32 logic. It resolves the foreground window handle via `dragonfly.Window.get_foreground()`, wraps the HWND inside `pyvda.AppView`, executes the pinning method, and sends visual confirmation messages to `printer.out` for display in the Caster HUD.

### B. Functional Capabilities Matrix

| Command Function | Underlying PyVDA Call | Behavior | Target Scope |
| :--- | :--- | :--- | :--- |
| `pin_current_window()` | `AppView(hwnd).pin()` | Pins the foreground window across all virtual desktops. | Single window instance (HWND). |
| `unpin_current_window()` | `AppView(hwnd).unpin()` | Unpins the foreground window, restricting it to its active desktop. | Single window instance (HWND). |
| `toggle_pin_current_window()` | `view.is_pinned()` query, then `unpin()` or `pin()` | Flips the pinned state of the foreground window. | Single window instance (HWND). |
| `pin_current_app()` | `AppView(hwnd).pin_app()` | Pins all existing and future windows of the active application. | Entire process / AUMID. |
| `unpin_current_app()` | `AppView(hwnd).unpin_app()` | Unpins the application from all virtual desktops. | Entire process / AUMID. |
| `toggle_pin_current_app()` | `view.is_app_pinned()` query, then `unpin_app()` or `pin_app()` | Flips the pinned state of the active application. | Entire process / AUMID. |

---

## 3. Phonetic Coarticulation & Acoustic Misrecognition Analysis

The initial voice spec for pinning a window was formulated as:
`([toggle] pin | unpin) window [all work [spaces]]`

In daily operation under Kaldi, speaking `pin window` resulted in consistent misrecognition as `new window`. Because active application rules in browsers and text editors bind `new window` to hotkeys like `Ctrl+N` or `Ctrl+Shift+N`, this misrecognition triggered disruptive side effects.

### A. Phonemic Breakdown

The International Phonetic Alphabet (IPA) transcriptions for the competing phrases are as follows:

| Phrase | Orthographic Tokens | IPA Transcription | Syllable Count |
| :--- | :--- | :--- | :--- |
| Target Phrase | `pin window` | `/p ɪ n   w ɪ n d oʊ/` | 3 syllables |
| Competing Hypothesis | `new window` | `/n j uː   w ɪ n d oʊ/` or `/n uː   w ɪ n d oʊ/` | 3 syllables |

```
Target:     / p  ɪ  n / + / w  ɪ  n  d  oʊ /
            [plosive] [vowel] [nasal]   [approximant] ...
Competing:  / n  j  uː / + / w  ɪ  n  d  oʊ /
            [nasal] [glide] [vowel]     [approximant] ...
```

### B. Acoustic Mechanics of Coarticulation

The confusion between `pin window` and `new window` stems from three physiological and acoustic factors:

1. **Weakened Plosive Burst:**
   The voiceless bilabial stop `/p/` relies on a transient burst of acoustic energy produced upon release of lip closure. This burst lasts only 10 to 25 milliseconds. In rapid, connected, or relaxed speech, speakers often soften the stop closure or produce an incomplete release. Without a strong high-frequency burst, the initial acoustic onset is dominated by the voiced nasal formant of the subsequent phonemes.

2. **Inter-Word Nasal-to-Approximant Transition:**
   In `pin window`, the alveolar nasal `/n/` transitions directly into the voiced labio-velar approximant `/w/`. The mouth moves from an alveolar tongue touch directly to rounded lips. In connected speech, this transition creates a continuous formant glide (`F1` and `F2` shift) that acoustic feature extractors (e.g., Mel-frequency cepstral coefficients, or MFCCs) evaluate as nearly indistinguishable from the glide `/n/` → `/j/` → `/u/` in `new`.

3. **Shared Terminal Trajectory:**
   Both phrases share the exact same two-syllable tail `/w ɪ n d oʊ/`. Consequently, the acoustic decoder has only the first 150 to 200 milliseconds of speech to differentiate the two candidates.

### C. Language Model Priors and Decoder Trellis Dynamics

Kaldi speech decoders determine the winning token sequence $\hat{W}$ by evaluating the maximum a posteriori probability over acoustic observations $O$:

$$
\hat{W} = \arg\max_{W} P(O \mid W) \cdot P(W)
$$

where:
- $P(O \mid W)$ represents the acoustic model likelihood.
- $P(W)$ represents the n-gram language model prior probability.

In standard speech corpora and developer-oriented language models:
- The bigram probability $P(\text{window} \mid \text{new})$ is exceptionally high. The phrase `new window` appears throughout web browsers, terminal emulators, code editors, file explorers, and general operating system documentation.
- The bigram probability $P(\text{window} \mid \text{pin})$ is near zero. In standard English corpora, `pin` functions primarily as a noun or precedes prepositional phrases (`pin to taskbar`, `pin on map`).

When a speaker utters `pin window` with a slightly softened `/p/`, the acoustic likelihood $P(O \mid \text{pin window})$ is only marginally higher than $P(O \mid \text{new window})$. When multiplied by the language model priors, the prior weight for `new window` dominates the Viterbi trellis calculation. The decoder selects `new window`, and the speech engine dispatches an unintended command.

---

## 4. Grammar Ergonomics & Syntactic Trade-Offs

To eliminate the recognition failure, the voice grammar can be restructured. Multiple approaches exist, each presenting distinct trade-offs between acoustic robustness, syntactic consistency, and brevity.

### A. Syntactic Consistency in Caster Core Grammar

Within `WindowManagementRule`, window control commands follow a strict structural pattern:

```python
"window maximize":        R(Function(window_mgmt.maximize_window)),
"window minimize":        R(Function(window_mgmt.minimize_window)),
"window restore":         R(Function(window_mgmt.restore_window)),
"window close":           R(Function(window_mgmt.close_window)),
"window center":          R(Function(window_mgmt.center_window)),
"window (right | left)":   R(Function(window_mgmt.snap_window)),
```

Every standard window management command in Caster uses the **Noun-First** structure: `window <action/direction>`.

The initial pinning specification (`pin window`) violated this convention by introducing a **Verb-First** structure (`<action> window`). This structural departure created cognitive friction and exposed the grammar to the acoustic collision with `new window`.

### B. Structural Options Evaluated

The following table evaluates four structural alternatives for window pinning:

| Specification Pattern | Grammar Example | Acoustic Collision Risk | Caster Grammar Alignment | Syllable Count | Practical Ergonomics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Verb-First (Original)** | `pin window`<br>`unpin window` | **High:** Collides with `new window`. | Inconsistent with `window maximize/minimize`. | 3 syllables | Natural in colloquial English, but high failure rate. |
| **2. Noun-First (Recommended)** | `window pin`<br>`window unpin` | **Zero:** `window new` does not exist in grammar. | Fully consistent with existing window rules. | 3 syllables | Fast, deterministic, matches Caster structural norms. |
| **3. Acoustic Decoupler Token** | `pin this window`<br>`unpin this window` | **Zero:** `this` introduces strong `/ð ɪ s/` barrier. | Inconsistent with existing window rules. | 4 syllables | Retains verb-first phrasing; extra syllable slows execution. |
| **4. Bi-Directional Dual Grammar** | `[window] pin [this] window` | **Low to Moderate:** Depends on which variant is spoken. | Flexible across user mental models. | 3 to 4 syllables | Increases grammar rule complexity and trellis branching. |

### C. Why Noun-First (`window pin`) Eliminates the Collision

Adopting the noun-first syntax `window pin` eliminates the misrecognition through three mechanisms:

1. **Prefix Gating in the Search Trellis:**
   When the utterance begins with `window` (`/w ɪ n d oʊ/`), the decoder branches immediately into the `window` prefix node of `WindowManagementRule`. The competing hypothesis `new window` is excluded at the root because it begins with `/n j uː/`.

2. **No Grammatical Competitor:**
   There is no command in Caster named `window new`. Once `window` is recognized, the decoder can only transition to valid suffixes: `pin`, `unpin`, `maximize`, `minimize`, `restore`, `close`, `center`, or directional snaps.

3. **Syllabic and Phonetic Distance from Existing Suffixes:**
   Within the `window <action>` family, `pin` (`/p ɪ n/`) has high phonetic separation from the other suffixes:
   - `window minimize`: 5 syllables. `/m ɪ n ɪ m aɪ z/` vs `/p ɪ n/`.
   - `window maximize`: 5 syllables. `/m æ k s ɪ m aɪ z/` vs `/p ɪ n/`.
   - `window restore`: 4 syllables. `/r ɪ s t ɔː r/` vs `/p ɪ n/`.
   - `window close`: 3 syllables. `/k l oʊ z/` has a velar stop onset and sibilant coda, presenting no overlap with the bilabial nasal structure of `/p ɪ n/`.

### D. Acoustic Decoupling via Demonstrative Pronouns

If a verb-first phrasing is preferred by an individual user, inserting the demonstrative pronoun `this` (`pin this window`) resolves the coarticulation issue:

```
Spoken:  / p ɪ n /  +  / ð ɪ s /  +  / w ɪ n d oʊ /
          [pin]           [this]             [window]
```

The word `this` introduces two distinct acoustic features:
1. A voiced dental fricative `/ð/` at the onset.
2. An alveolar sibilant fricative `/s/` at the coda, characterized by high-frequency turbulent noise (5 kHz to 8 kHz).

This high-frequency sibilant boundary completely prevents the nasal murmur of `pin` from blending into the approximant onset of `window`. Even if `/p/` is weakened, the sequence cannot match `new window`.

---

### E. Phonetic & Collision Analysis of Application Pinning (`pin app` vs `app pin`)

While `window pin` provides an effective noun-first solution for window-level scoping, evaluating application-level pinning reveals a severe symmetry dilemma.

#### 1. Acoustic Vulnerabilities of Verb-First `pin app`
The phrase `pin app` is phonetically transcribed as `/p ɪ n   æ p/`. It exhibits significant acoustic instability in connected speech:
- **Resyllabification across Word Boundaries:** In conversational cadence, the alveolar nasal coda `/n/` links across the word boundary directly into the lax open vowel `/æ/`. The speech engine perceives `[p ɪ . n æ p]`.
- **Phonetic Collisions:** In noisy environments or during relaxed enunciation, `[p ɪ . n æ p]` easily collides with phonetically adjacent phrases:
  - `pin up` (`/p ɪ n ʌ p/`)
  - `chin up` (`/tʃ ɪ n ʌ p/`, where the affricate `/tʃ/` burst is confused with an unvoiced plosive `/p/`)
  - `pen up` (`/p ɛ n ʌ p/`)
- **Acoustic Mass Deficit:** The phrase consists of only two short syllables (lasting roughly 200 to 250 milliseconds) composed entirely of short lax vowels bounded by stops. Short phrases have low acoustic mass, leaving the decoder vulnerable to energy cutoffs and spurious insertion errors.

#### 2. The Failure Mode of Noun-First `app pin`: Collision with 'Open'
Attempting to enforce syntactic uniformity by transposing `pin app` into noun-first `app pin` creates a far more hazardous collision:

```
Orthography:     app pin
Phonemic:        / æ p   p ɪ n /
Phonetic:        [ æ . p ɪ n ]   (bilabial stop gemination)
Collision:       / oʊ p ə n /    ('open')
```

1. **Stop Gemination:** When `/æ p/` is followed immediately by `/p ɪ n/`, the speaker does not release the first `/p/` before forming the second. The articulators form a single, prolonged bilabial closure released once: `[æ . p ɪ n]`.
2. **Acoustic Overlap with 'Open':** The acoustic envelope of `[æ . p ɪ n]` matches `open` (`/oʊ p ə n/` or `[oʊ . p ɪ n]`), particularly in casual speech where unstressed vowels neutralize to a schwa or near-close front vowel.
3. **Catastrophic Voice Command Impact:** Unlike `new window`, which only impacts browsers or editors, `open` is a primary global dispatch keyword across nearly every voice grammar (`open <target>`, `open file`, `open settings`). A false positive match against `open` hijacks system execution and causes unintended application launches.

---

### F. The Structural Symmetry Dilemma & The Unified 'this' Standard

Evaluating the two scoping tiers exposes an architectural contradiction:
- Noun-first works cleanly for windows (`window pin` avoids collisions because `window` has high acoustic mass and no grammatical competitor exists).
- Noun-first fails for applications (`app pin` directly collides with `open`).
- Using `window pin` alongside `pin app` creates an asymmetric hybrid grammar that increases cognitive load and causes hesitations during dictation.

#### Comparative Matrix Across Scoping Forms

| Scoping Level | Grammar Candidate | Phonetic Trajectory | Primary Collision Risk | Practical Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **Window** | `pin window` | `/p ɪ n w ɪ n d oʊ/` | `new window` (`Ctrl+N` trigger) | Unacceptable failure rate. |
| **Window** | `window pin` | `/w ɪ n d oʊ p ɪ n/` | None (no `window new` rule) | Highly robust, but creates asymmetry if `app` cannot match. |
| **Window** | `pin this window` | `/p ɪ n ð ɪ s w ɪ n d oʊ/` | None (`/ð ɪ s/` blocks glide) | 100% robust; preserves natural verb-first cadence. |
| **Application** | `pin app` | `/p ɪ n æ p/` | `pin up`, `chin up` | Low acoustic mass; vulnerable to background noise. |
| **Application** | `app pin` | `/æ p p ɪ n/` | `open`, `happen` | Catastrophic collision with global `open` commands. |
| **Application** | `pin this app` | `/p ɪ n ð ɪ s æ p/` | None (`/ð ɪ s/` breaks gemination) | 100% robust; preserves natural verb-first cadence. |

#### 3. Empirical In-Vivo Telemetry: The 'App' Collapse & Trellis Bloat
During live voice testing under Kaldi speech models, empirical trials revealed two further acoustic failure modes:

1. **`pin app` Collides with `shin up`:**
   In Caster's continuous command recognition (CCR) navigation, `shin` serves as the alphabet specifier for the Shift modifier, and `shin up` dispatches `Shift+Up`. In rapid connected speech, the unvoiced bilabial plosive `/p/` into nasal `/ɪ n/` was repeatedly misidentified as the postalveolar fricative `/ʃ ɪ n/`, executing accidental text selection instead of workspace pinning.

2. **`pin this app` Collides with `press up`:**
   When attempting `pin this app` to introduce an acoustic separator, the brief duration of monosyllabic `app` (`/æ p/`) combined with the sibilant `/s/` coda of `this` caused the acoustic decoder to match `press up` (`/p r ɛ s ʌ p/`). The phonetic sequence `/ð ɪ s æ p/` had insufficient acoustic separation from `/ɛ s ʌ p/`.

3. **Premature Endpointing via Verbose Suffixes:**
   Appending optional suffixes such as `[all work [spaces]]` expanded the search trellis significantly. Because Kaldi uses fixed end-of-speech silence thresholds (padding), speaking a long compound phrase often resulted in the engine cutting off and finalizing recognition on an early prefix before the speaker finished the trailing tokens.

#### 4. The Final Production Grammar: Minimalist Syntax & Quadrisyllabic Expansion
To eliminate all empirical collisions and prevent search trellis bloat:
- **Bi-Directional Window Pinning:** Support both `window ([toggle] pin | unpin)` and `([toggle] pin | unpin) window`. This gives users the option between Caster's standard noun-first convention and colloquial verb-first phrasing.
- **Quadrisyllabic Application Expansion:** Replace the short monosyllabic token `app` (`/æ p/`) with the full quadrisyllabic noun `application` (`/ˌ æ p l ɪ ˈ k eɪ ʃ ə n/`). The 4-syllable phonetic mass provides complete acoustic immunity from `shin up`, `press up`, and `open`.
- **Suffix Pruning:** Completely remove `[all work [spaces]]` to eliminate trellis branching and prevent premature endpointing.

```python
# Final simplified production specification
"([toggle] pin | unpin) window":
    R(Function(virtual_desktops.toggle_pin_current_window)),
"window ([toggle] pin | unpin)":
    R(Function(virtual_desktops.toggle_pin_current_window)),
"([toggle] pin | unpin) [this] application":
    R(Function(virtual_desktops.toggle_pin_current_app)),
```

---

## 5. Upstream Contribution Strategy & Dependency Coordination

Contributing features to open-source speech and accessibility tooling requires coordinated multi-repository changes and an understanding of maintainer priorities.

### A. Maintainer Context and Contribution Norms

Maintainers of foundational accessibility frameworks (such as Dragonfly and Caster) manage codebases with high stability requirements and legacy constraints. Recent surges in automated pull requests from accounts scanning bounty platforms have made maintainers cautious regarding low-context contributions.

Key principles for successful upstream integration:
- **Demonstrate Prior Groundwork:** Provide concrete technical breakdowns, cite existing code architecture, and verify that changes do not regress existing configurations.
- **Architectural Separation:** Ensure operating system-specific APIs (e.g., Windows COM virtual desktop interfaces) remain isolated behind clean platform abstraction barriers.
- **Avoid Anti-Patterns:** Prefer robust architectural solutions over temporary workarounds.

### B. Upstream PyVDA Bug: XAML Island Sub-AUMID Multi-Window Pinning

Caster relies on the external Python library `pyvda` for virtual desktop interactions. During testing of application pinning (`pin app`), a significant limitation was identified in `pyvda`:

1. **The Mechanism:** Windows Virtual Desktop Manager (`twinui.pcshell.dll`) exposes the COM interface `IVirtualDesktopPinnedApps`. It manages pinned application states through exact string comparison (`wcscmp`) of AppUserModelIDs (AUMIDs).
2. **The Defect:** In modern Windows applications utilizing XAML Islands or multi-window packaging (such as Windows Terminal or Antigravity IDE), secondary windows are assigned synthetic per-window sub-AUMIDs:
   `Microsoft.WindowsTerminal_8wekyb3d8bbwe!App~Wh~w00620A28`
   where `~Wh~w<HEX_HWND>` encodes the window handle.
3. **The Consequence:** When `pyvda.AppView.pin_app()` was invoked on a secondary window, it registered the synthetic sub-AUMID in the Windows registry key `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VirtualDesktops\PinnedApps`. Because other windows of the same application use different AUMIDs, they were not pinned. Furthermore, when the secondary window closed, its HWND became invalid, leaving permanent orphan entries in the registry.

### C. Coordinated Upstream Resolution

To resolve the issue cleanly, work was divided across two repositories:

1. **PyVDA Upstream Refactor (Repository: `amirf147/pyvda`, branch `fix/multi-window-app-pinning`, commit `66d3f64`):**
   - Refactored `AppView.app_id` to reliably return string values.
   - Added `AppView.base_app_id` to strip the `~Wh~w<HEX_HWND>` suffix and identify the canonical application package.
   - Updated `pin_app()`, `unpin_app()`, and `is_app_pinned()` to pin the base AUMID for future windows while using `IVirtualDesktopPinnedApps::PinView` for active secondary sub-views, avoiding registry pollution.
   - Introduced `sync_pinned_apps()` to reconcile newly opened sub-views across workspace transitions.

2. **Caster Upstream Feature (Repository: `amirf147/Caster`, branch `feat/virtual-desktop-pinning`, commit `b549ca2b`):**
   - Implemented `pin_current_window()`, `unpin_current_window()`, `toggle_pin_current_window()`, `pin_current_app()`, `unpin_current_app()`, and `toggle_pin_current_app()` in `windows_virtual_desktops.py`.
   - Added platform fallbacks in `virtual_desktops.py`.
   - Routed execution status through `printer.out` for Caster HUD display.
   - Exposed the commands in `WindowManagementRule`.

3. **Dependency Decoupling:**
   The Caster feature branch uses standard `pyvda.AppView` methods (`pin()`, `unpin()`, `pin_app()`, `unpin_app()`, `is_pinned()`, `is_app_pinned()`). If Caster merges this feature before PyVDA publishes the multi-window fix to PyPI:
   - Window pinning operates with full functionality across all PyVDA versions.
   - Application pinning operates correctly for single-window applications and classic Win32/Gecko applications on older PyVDA versions.
   - Installing the patched PyVDA resolves multi-window XAML Island pinning without requiring further modifications to Caster core code.

### D. Comparison with WinStasis Architecture

To verify whether other virtual desktop utilities suffered from the same sub-AUMID defect, the codebase of **WinStasis** (`WinStasis repository`) was examined:

- **Finding:** WinStasis is completely unaffected by the sub-AUMID issue.
- **Architectural Reason:** WinStasis interacts with the Windows Shell exclusively via `IVirtualDesktopPinnedApps::PinView(IApplicationView*)` using native window handles (`HWND`). It does not invoke `PinAppID(LPCWSTR)` and does not query or evaluate AUMIDs. Because `PinView` operates on the unmanaged shell view pointer in memory, it binds directly to the window instance regardless of how the application framework formats its AppUserModelID.

---

## 6. Implementation and Verification Protocol

### A. Testing Procedure

To verify pinning functionality and grammar reliability, execute the following test protocol:

1. **Phonetic Recognition Verification:**
   - Speak `window pin` 10 times in conversational cadence with an active browser window open.
   - Confirm that the Caster HUD displays: `Window pinned to all workspaces`.
   - Confirm that zero browser windows are spawned (0% collision with `new window`).
   - Switch to a secondary virtual desktop (`work 2`) and verify that the pinned window remains visible.

2. **Window Unpin Verification:**
   - On the secondary virtual desktop, speak `window unpin` or `window pin` (toggle).
   - Confirm HUD output: `Window unpinned from all workspaces`.
   - Switch back to `work 1` and verify that the window is no longer visible on `work 2`.

3. **Multi-Window Application Pinning Verification:**
   - Open a primary Windows Terminal window on Virtual Desktop 1.
   - Open a secondary Windows Terminal window on Virtual Desktop 1.
   - Focus the secondary window and speak `pin app` or `toggle pin app`.
   - Switch to Virtual Desktop 2.
   - Verify that both Windows Terminal windows are visible on Virtual Desktop 2.
   - Inspect registry key `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VirtualDesktops\PinnedApps` to confirm that only the base package identifier (`Microsoft.WindowsTerminal_8wekyb3d8bbwe!App`) is stored, with no transient hex handle keys.

---

## 7. Cross-Reference Index

- **PyVDA Multi-Window Architecture Deep Dive:** [docs/pyvda/003_pyvda_multi_window_xaml_island_pinning_architecture.md](../pyvda/003_pyvda_multi_window_xaml_island_pinning_architecture.md)
- **PyVDA Adversarial Audit & Resilient Client Design:** [docs/pyvda/004_adversarial_audit_and_hardened_com_architecture.md](../pyvda/004_adversarial_audit_and_hardened_com_architecture.md)
- **PyVDA Subsystem Hub:** [docs/pyvda/README.md](../pyvda/README.md)
- **PyVDA RPC & COM Lifecycle:** [docs/pyvda/001_pyvda_rpc_and_com_lifecycle_analysis.md](../pyvda/001_pyvda_rpc_and_com_lifecycle_analysis.md)
- **Caster Documentation Hub:** [docs/README.md](../README.md)
- **Caster Repository Brain (SSOT):** [docs/context/repository-brain.md](../context/repository-brain.md)
- **Technical Journey Log:** [docs/history/technical_journey.md](../history/technical_journey.md)
