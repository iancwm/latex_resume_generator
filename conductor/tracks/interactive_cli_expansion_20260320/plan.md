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

## Phase 3: Expanded Input Flows (Skills & Projects) [checkpoint: 30db630]

1. **Skills Section**
   - [x] Task: Write failing tests for the `Skills` input flow. [74731d4]
   - [x] Task: Implement the `Skills` menu (categories and keyword lists). [b4ec185]
2. **Projects Section**
   - [x] Task: Write failing tests for the `Projects` input flow. [d2b11c8]
   - [x] Task: Implement the `Projects` menu (URL and highlights list). [8bb24c6]
3. **Phase Checkpoint**
   - [x] Task: Conductor - User Manual Verification 'Skills & Projects Flows' [30db630] (Protocol in workflow.md)

## Phase 4: Validation & Consistency [checkpoint: 97623e7]

1. **Input Validation Logic**
   - [x] Task: Write failing tests for date format (`YYYY-MM`) and required field validation. [73801f1]
   - [x] Task: Implement reusable validation helpers in `src/main.py`. [73801f1]
   - [x] Task: Integrate validation into the interactive input prompts. [73801f1]
2. **Bullet Point Consistency Check**
   - [x] Task: Write failing tests for bullet point period consistency across lists. [df99201]
   - [x] Task: Implement a post-input check for list punctuation consistency. [df99201]
3. **Enhanced Draft Management**
   - [x] Task: Implement deep merge logic for loading existing YAML data. [97623e7]
   - [x] Task: Update save logic to use `drafts/` folder and append user's first name to filenames. [97623e7]
   - [x] Task: Write tests for deep merging and renamed draft files. [97623e7]
4. **Phase Checkpoint**
   - [x] Task: Conductor - User Manual Verification 'Validation & Consistency' [97623e7] (Protocol in workflow.md)
