# 🌐 **AI Horary Interpretation System — API Architecture Document**

## **0. Overview**

This document describes the architecture of an AI-driven horary interpretation system.
The system integrates multiple technical components:

* Natural Language Processing (NLP)
* Context-aware AI
* GPS and time-based contextual data
* Lightweight psychological trait inference (OCEAN)
* Horary astrological chart calculation
* LLM-based symbolic interpretation
* Conversational UX with clarification loops

The goal is to transform messy, emotional, or contradictory user input into a clear, horary-compatible question, generate raw astrological data using location and timestamp, and produce a human-readable, culturally appropriate interpretation using LLMs.

---

## **1. System Architecture Overview**

```
User Input
    ↓
Context Intake Layer (Language, GPS, Timestamp, OCEAN)
    ↓
Question Refinement Layer (NLP preprocessing)
    ↓
Clarification UX Loop (user confirmation)
    ↓
Horary Chart Generator (raw psycho-astronomical data)
    ↓
LLM Interpretation Layer (raw → narrative meaning)
    ↓
Final Response to User
```

---

## **2. Context Intake API**

Collects all contextual signals required for horary interpretation and tailored UX.

**Inputs**

* `user_text`
* `language` (auto-detected)
* `gps_coordinates` (opt-in)
* `timestamp`
* `consent_flags`

**Processing**

* Language detection
* Timezone resolution
* OCEAN personality signal estimation (internal only)

**Outputs**

```json
{
  "language": "ko-KR",
  "timezone": "Asia/Seoul",
  "timestamp": "2025-01-21T23:41:15+09:00",
  "gps": { "lat": 37.5665, "lon": 126.9780 },
  "ocean_estimate": {
    "O": "medium",
    "C": "low",
    "E": "low",
    "A": "high",
    "N": "high"
  }
}
```

---

## **3. Question Refinement API**

Converts unstructured or emotionally overloaded input into a single actionable question.

**Tasks**

1. Strip emotional noise
2. Extract candidate questions
3. Cluster semantically similar questions
4. Determine core repeated theme
5. Produce one canonical horary question
6. Generate 2–3 alternative options for user confirmation

**Output Example**

```json
{
  "primary_question": "Will my relationship with this person improve?",
  "options": [
    "Is it okay if I contact them now?",
    "Does this person still have interest in me?",
    "Should I let go of this relationship?"
  ]
}
```

---

## **4. Clarification UX API**

Ensures question correctness, stabilizes ambiguity, and prevents misinterpretations.

**Input:**

* primary question + user selection

**Output:**

```json
{
  "confirmed_question": "Will my relationship with this person improve?"
}
```

---

## **5. Horary Chart Generation API (Astro Engine)**

Generates assembly-level raw data based on timestamp and GPS.

**Uses:**

* Swiss Ephemeris / pyswisseph
* flatlib
* astronomy-engine

**Output Example**

```json
{
  "ascendant": "23° Taurus",
  "midheaven": "5° Aquarius",
  "planets": {
    "Moon": { "pos": "12° Cancer", "house": 3 },
    "Venus": { "pos": "28° Capricorn", "house": 8 },
    "Mars": { "pos": "7° Capricorn", "house": 8 }
  },
  "aspects": [
    { "between": ["Moon", "Saturn"], "type": "trine", "orb": 3 },
    { "between": ["Venus", "Mars"], "type": "conjunction", "orb": 1 }
  ]
}
```

---

## **6. LLM Interpretation API**

Maps symbolic data → human language narrative.

**Inputs**

* confirmed question
* raw astro data
* language
* OCEAN estimate

**Output**

```json
{
  "interpretation": 
    "The Moon–Saturn trine shows emotional stability returning between you two..."
}
```

---

## **7. Ethical Considerations & User Consent**

All contextual data (GPS, timestamp, psychological inference) must be processed transparently and only with explicit user consent.
No sensitive data should be stored unless the user permits it.

---

# **8. Educational Value (What You Learn by Designing This System)**

(*Separated as its own subtopic, as requested.*)

Working through this system—even purely as a design exercise—provides hands-on exposure to several advanced areas of AI system engineering:

### **8.1 NLP & Text Understanding**

* Extracting meaning from long, emotional, contradictory input
* Designing question-refinement systems
* Prompt engineering for structured reasoning

### **8.2 Context-Aware AI Development**

* Integrating timestamp, GPS, language locale, and personality signals
* Building “context-sensitive” AI pipelines

### **8.3 Psychological Signal Modeling**

* Lightweight OCEAN inference from natural language
* Tone adaptation based on personality cues

### **8.4 Data Pipeline Architecture**

* Transforming raw numerical/symbolic data into abstractions
* Multi-stage pipeline design
* Clean separation of concerns across modules

### **8.5 Symbolic-to-Natural Language Mapping**

* Converting raw astrological coordinates (assembly-level) into
  coherent, human-friendly narrative interpretation

### **8.6 Conversational UX & AI Interaction Design**

* Designing clarification loops
* Reducing user cognitive load
* Creating culturally appropriate storytelling in the user’s language

### **8.7 Responsible AI & Privacy Handling**

* Building systems that respect consent, privacy, and sensitive context
* Real-world ethical design practices

**In short:**
This system is an ideal micro-project for learning *modern AI product engineering* with a real, multi-layered workflow.

