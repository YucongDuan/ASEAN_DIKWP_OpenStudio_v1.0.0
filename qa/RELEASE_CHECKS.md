# Release checks — v1.0.0 / 2026-09-16

This report records tests actually executed for the delivered source. It is not an independent certification or a claim that all catalogued upstream repositories were run.

| Suite | Passed | What was exercised |
|---|---:|---|
| Node teaching/core tests | 83 | Multilingual concept lookup, ranking and reasons, prerequisite order and cycles, every lesson quiz, unit conversion and mismatches, 3-No conditions, purpose/action decisions, ablation, path alternatives, project validation, manifests and ZIP generation. |
| Python API, upstream and HTTP tests | 80 | WSGI request handling, real loopback HTTP, salted passwords, sessions, CSRF/origin/host, private ownership, optimistic versions, course membership, teacher feedback and fixed snapshots; archive safety, mock pin/fetch, metadata pagination and merge behavior. |
| Chromium UI interactions | 59 | All 13 language selectors, complete Vietnamese lesson reading, all 12 self-checks, repository comparison, learning route, all four labs, changed purpose and ablation, saved records, replay, actual ZIP download, source/book/report navigation, mobile layout, teacher/student workflow and feedback. |
| Exported student Python example | 5 | Unit equivalence, purpose changes, unknown units, currency differences and nonfinite values. |

The four suites contain **227 passing checks** as grouped above. Per-suite logs and machine-readable JSON are retained in this directory. The exported source ZIPs passed CRC checks. All lesson→repository, lesson→lecture, scenario→repository, book→source and lecture→source links were checked against the bundled data.

## Execution scope

The Chromium environment disallows normal URL navigation through managed browser policy. The UI harness therefore uses `set_content` to render the full delivered offline HTML and an explicitly declared in-memory localStorage test double. For class interactions, an explicit test bridge invokes the real Python WSGI app; it is not a mocked set of successful API responses. Separate Python tests exercise actual loopback HTTP, cookies, login, save/read and static serving.

Accordingly, the release does **not** claim a full browser-over-network deployment test or actual browser disk persistence in this managed environment. Storage failure handling is explicit in the application. No browser policy was changed. The screenshots are real renders of the shipped UI in this harness, not design mockups.

GitHub connector reads inspected the author directory and PACT source documentation. The standalone runtime environment could not complete an external GitHub download. The source-fetch and catalogue-sync scripts were tested with controlled transport responses and malicious archive fixtures. Real network connectivity and a real commit-specific download should be checked on the machine that will run those optional commands.

No campus server deployment, remote GitHub publication, actual external message sending, clinical use or independent educational-outcome study is represented as performed. The sample project is synthetic and runs locally.

## Re-run

From the repository root:

```bash
python scripts/check_release.py
# Developer browser dependency: Playwright and a Chromium executable.
python scripts/check_release.py --browser
```

The shipped browser harness uses `/usr/bin/chromium` as found in this environment; adjust `executable_path` in `tests/browser_check.py` to your own browser installation if necessary. New browser executions outside this managed environment may also add a conventional network end-to-end test.
