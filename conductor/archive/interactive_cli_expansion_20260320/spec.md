# Specification: Flesh Out Interactive Menu and Input Workflow

## Overview
This track aims to expand the current interactive CLI builder to support all major resume sections (Work Experience, Education, Skills, and Projects). It will also introduce the ability to load and edit existing YAML files, improve list handling with sentinel values, and add validation for data consistency.

## Functional Requirements
- **Interactive Menu Expansion:**
  - Implement full input flows for:
    - **Work Experience:** `company`, `position`, `location`, `startDate`, `endDate`, `summary` (list).
    - **Education:** `institution`, `area`, `location`, `startDate`, `endDate`, `score`, `honors` (list), `courses` (list).
    - **Skills:** `category`, `keywords` (list).
    - **Projects:** `name`, `description`, `url`, `highlights` (list).
- **List Input Workflow:**
  - When entering a list (e.g., job bullet points or skills), the user should be prompted to enter items one by one.
  - Entering a specific sentinel value (e.g., "done" or an empty string) should finish the list input.
- **File Handling (Load & Edit):**
  - Add the ability to load existing `public.yaml` and `private.yaml` files into the interactive session.
  - If files don't exist, start with a fresh template.
  - Allow the user to navigate and edit specific fields or sections without re-entering all data.
- **Data Validation:**
  - **Date Format:** Ensure `startDate` and `endDate` follow the `YYYY-MM` or `Present` format.
  - **Required Fields:** Ensure critical fields like `name`, `email`, `company`, `position`, and `institution` are not left empty.
  - **Bullet Point Consistency:** For list inputs (like job summaries or project highlights), validate that either all items end with a period or none of them do. Prompt the user to correct inconsistencies.

## Acceptance Criteria
- [ ] The interactive menu successfully captures all fields for Work, Education, Skills, and Projects.
- [ ] List inputs can be completed using a sentinel value.
- [ ] Existing YAML files can be loaded, modified, and saved without losing unrelated data.
- [ ] The CLI rejects invalid date formats (non `YYYY-MM`).
- [ ] The CLI enforces required fields.
- [ ] The CLI warns or rejects inconsistent bullet point punctuation within a single list.
- [ ] All changes are reflected in `draft_public.yaml` and `draft_private.yaml` (or the original files if requested).

## Out of Scope
- Visual design changes to the LaTeX templates.
- Automatic fetching of data from external APIs (e.g., LinkedIn).
