# JSON API

All endpoints are same-origin. Writes require `application/json`; authenticated writes also require the `X-CSRF-Token` from login/session. Browser cookies are HttpOnly, SameSite=Strict and Secure when the configured origin is HTTPS. The application validates Host and any supplied Origin. There is no permissive cross-origin API.

| Method | Path | Contract |
|---|---|---|
| GET | /api/health | Version and service status |
| GET | /api/session | Current user, role, CSRF and registration availability |
| POST | /api/register | username, password; creates a student |
| POST | /api/login | username, password; returns user and CSRF, sets session cookie |
| POST | /api/logout | Ends current session |
| GET | /api/projects | Own projects only |
| PUT | /api/projects/{id} | Valid project with expected version; returns next version |
| DELETE | /api/projects/{id} | Own project and its saved revisions |
| GET | /api/projects/{id}/history | Own saved revisions |
| GET / POST | /api/courses | List joined/owned courses; teachers create with name and brief |
| POST | /api/courses/join | code |
| POST | /api/courses/{id}/submit | project_id; snapshots the caller's saved project |
| GET | /api/courses/{id}/submissions | Teacher sees own course; students see only their submissions |
| POST | /api/submissions/{id}/review | Owning teacher supplies comment and optional rubric |

A stale project version returns 409 without overwriting. Invalid schema returns 400. Missing authentication returns 401. Missing CSRF or disallowed role/origin returns 403. Unauthorized access to another user's project is indistinguishable from not-found (404). Oversized bodies return 413. Login attempts are rate-limited in-process.

The optional rubric accepts only understanding, choice, inheritance, validation and innovation integers from 0 to 4. It does not calculate an overall learner rating. The shipped UI uses comments. Maximum request body is 700,000 bytes. Project text and experiment histories have separate bounds. See `app/server.py` and executable tests for the complete contract.
