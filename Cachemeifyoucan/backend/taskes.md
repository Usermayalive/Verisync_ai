# Pending Tasks Before Final Push

This file tracks the remaining tasks we need to complete before pushing to the `backend` branch, to ensure nothing is missed or executed prematurely.

- `[x]` Run `git fetch` to check for remote updates from Person B on the `main` branch.
- `[x]` Strip all comments from the existing backend Python code.
- `[/]` **Integration Bugfixes (Approved)**
    - `[x]` Update `QueryRequest` schema in `main.py`
    - `[x]` Append `x-api-key` security header to all UI calls
    - `[x]` Add `st.file_uploader` to UI and link to `/api/ingest`
    - `[x]` Patch session state logic in UI
    - `[x]` Implement `Helsinki-NLP` translation hook in pipelines
- `[x]` **Final Certification (76/76)**
    - `[x]` Create `test_requirements.py` for 11 MVP queries
    - `[x]` Overhaul `README.md` for production architecture
    - `[x]` Final verification and cleanup
