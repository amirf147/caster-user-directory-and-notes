[ 🏠 Docs Home ](../README.md) › [ 📁 Future Ideas ](001_caster_help_rule_and_context_aware_assist_architecture.md) › **004: Phonetic Collision Atlas & Grammar Verification Engine**

---

# Future Concept: Phonetic Collision Atlas & Grammar Verification Engine (004)

**Status:** Backlog Concept / Exploratory Note  
**Target Domain:** Speech recognition grammar design, acoustic phonetic modelling, automated command collision prevention.

---

## 1. Problem Statement & Motivation

Designing voice command grammars in Caster is currently an empirical trial-and-error process. A command phrase that appears syntactically logical to a developer often fails in daily use due to subtle acoustic coarticulation effects and language model priors:
- `pin window` silently triggers `new window` (`Ctrl+N` browser spawns).
- `pin app` triggers `shin up` (`Shift+Up` text selection).
- `pin this app` triggers `press up`.
- `app pin` collides with the global command `open`.

These failures stem from predictable phonetic patterns:
1. Low acoustic mass in short monosyllabic words (`app`, `pin`).
2. Consonant cluster reductions and coarticulation across word boundaries (`/n/` linking into `/w/` or `/æ/`).
3. Dominant language model priors in Kaldi and Dragon favoring common operating system vocabulary over custom grammar phrases.

Currently, developers discover these collisions only after shipping commands and experiencing false triggers. A systematic mechanism is needed to detect phonetic proximity before commands are deployed.

---

## 2. Conceptual Architecture

The proposed system consists of an offline phonetic analysis engine and a continuous integration grammar linter:

```
+-------------------------------------------------------------+
|               Caster Grammar Definitions                    |
|   (MappingRule, CCR rules, application navigation specs)    |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|             Grapheme-to-Phoneme (G2P) Converter            |
|   Converts command phrases to standard IPA / CMU phonemes   |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|              Phonetic Distance & Alignment Matrix           |
|   Evaluates Levenshtein distance on phonetic feature vectors |
|   (Manner, Place of Articulation, Voicing, Syllable count)  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|            Acoustic Collision Atlas & Linter Report         |
|   Flags high-risk pairs: distance < threshold AND prior > x |
+-------------------------------------------------------------+
```

---

## 3. Core Capabilities

1. **G2P Phonemic Mapping:**
   Extracts all active spoken phrases across global, CCR, and application-specific rules, converting them into phonetic strings using the CMU Pronouncing Dictionary or an automated G2P neural model.

2. **Feature-Weighted Phonetic Distance:**
   Instead of crude orthographic string distance, calculates weighted phonetic distance based on articulatory features:
   - Bilabial stop vs alveolar stop distance.
   - Nasal vowel glide transitions.
   - Syllable duration and acoustic mass weighting.

3. **Language Model Bias Weighting:**
   Cross-references candidate command pairs against common desktop command frequency dictionaries. If a proposed phrase has low acoustic distance to a high-frequency command (e.g. `new window`, `open`, `press up`), the linter raises a high-severity collision warning.

4. **Automated Structural Suggestions:**
   When a collision is flagged, the engine suggests structural mitigations:
   - Syllable expansion (e.g., expanding monosyllabic `app` to quadrisyllabic `application`).
   - Word order transposition (e.g., evaluating noun-first vs verb-first).
   - Insertion of demonstrative acoustic decouplers (e.g., `this`).

---

## 4. Implementation Boundary

This document serves solely as an architectural reference and conceptual backlog entry. Active development will proceed only if manual grammar design overhead justifies building automated acoustic linting tooling.
