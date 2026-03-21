# Implementation Plan - Interactive CLI Builder Expansion

## Phase 1: Foundation & Data Management [checkpoint: 7fa8062]

1. **File Loading & Persistence**
   - [x] Task: Write failing tests for loading existing `public.yaml` and `private.yaml` in the interactive session. [cfd0229]
   - [x] Task: Implement logic to load existing YAML data into the session's internal state. [cfd0229]
   - [x] Task: Update the `Save and Exit` logic to preserve existing data and save to `draft_public.yaml`/`draft_private.yaml`. [cfd0229]
2. **Phase Checkpoint**
   - [x] Task: Conductor - User Manual Verification 'Foundation & Data Management' [7fa8062] (Protocol in workflow.md)

## Phase 2: Expanded Input Flows (Work & Education) [checkpoint: 7bff860]

1. **Work Experience Section**
   - [x] Task: Write failing tests for the `Work Experience` input flow (multiple entries, nested bullet points). [c3cab54]
   - [x] Task: Implement the `Work Experience` menu with list handling (sentinel values for bullet points). [c3cab54]
2. **Education Section**
   - [x] Task: Write failing tests for the `Education` input flow (honors and courses lists). [c3cab54]
   - [x] Task: Implement the `Education` menu with list handling. [c3cab54]
3. **Phase Checkpoint**
   - [x] Task: Conductor - User Manual Verification 'Work & Education Flows' [7bff860] (Protocol in workflow.md)

## Phase 3: Expanded Input Flows (Skills & Projects)

1. **Skills Section**
   - [x] Task: Write failing tests for the `Skills` input flow. [74731d4]
   - [x] Task: Implement the `Skills` menu (categories and keyword lists). [b4ec185]
2. **Projects Section**
   - [x] Task: Write failing tests for the `Projects` input flow. [d2b11c8]
   - [~] Task: Implement the `Projects` menu (URL and highlights list).
3. **Phase Checkpoint**
   - [ ] Task: Conductor - User Manual Verification 'Skills & Projects Flows' (Protocol in workflow.md)

## Phase 4: Validation & Consistency

1. **Input Validation Logic**
   - [ ] Task: Write failing tests for date format (`YYYY-MM`) and required field validation.
   - [ ] Task: Implement reusable validation helpers in `src/main.py`.
   - [ ] Task: Integrate validation into the interactive input prompts.
2. **Bullet Point Consistency Check**
   - [ ] Task: Write failing tests for bullet point period consistency across lists.
   - [ ] Task: Implement a post-input check for list punctuation consistency.
3. **Phase Checkpoint**
   - [ ] Task: Conductor - User Manual Verification 'Validation & Consistency' (Protocol in workflow.md)
