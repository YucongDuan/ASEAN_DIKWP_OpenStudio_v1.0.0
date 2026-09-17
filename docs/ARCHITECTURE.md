# Architecture

## Runtime structure

```text
Browser (no dependencies, no model calls)
  UI + 13 locale packs + zh/en/vi lessons
  | learning atlas / repository compass / four labs
  | project studio / report and research library
  + localStorage (device-local drafts) + JSON/ZIP export
  |
  + optional same-origin JSON API, cookie session + CSRF
       WSGI Application → SQLite
       private projects → immutable submission snapshots → teacher feedback

Offline author tools
  catalogue sync → preserve teaching annotations
  manifest pin → commit-specific source archive → license/file-hash receipt
  build_web → self-contained offline HTML
```

## Main contracts

`openstudio.project/1` holds title, problem, beneficiary, five DIKWP fields, constraints, inherited/changed statements, hypothesis, evidence, reflection, selected repositories and experiment records. `id` is stable within a project; server version is incremented on save. Maximum six selected components and 100 experimental records are intentional classroom bounds.

`openstudio.upstream-lock/1` names the YucongDuan repository, exact canonical URL, selected role, license metadata and commit. A missing commit is labelled pin-required; it is never replaced by a fake hash. A pin call resolves the default branch once and records its current immutable SHA.

`openstudio.upstream-receipt/1` records archive SHA-256, source commit, file paths, hashes, retained license files and executed=false. A matching archive hash supports byte-level provenance, not software safety or research effectiveness.

## Recommendation

Query normalization uses Unicode NFKC and lowercase. The dictionary recognizes multilingual concept aliases. A transparent score combines concept coverage (65), lexical matching (15), curated starting-point status (10) and authored experience fit (10); an exact repository-name query receives a capped bonus. No star count is used. Tags and difficulty are editorial learning annotations, not inferred personal attributes. Unknown queries leave the catalogue accessible and explicitly report no concept match.

## Teaching engines

Alignment compares canonical entity and purpose fields, currency, physical dimension and normalized quantity. It supports a small explicit unit table and reports unknown units without invented conversion. 3-No preserves missing observations, interval intersection, hull and imprecision. Purpose/action checks separate purpose fidelity, permission and evidence while retaining helpful draft work. Semantic routing enumerates simple paths on an explicit illustrative graph and compares goal-specific cost/loss weights.

These are independently implemented teaching kernels inspired by the research methods, not replicas or universal validators of the upstream projects. The generated Python scaffold is a smaller mass/volume subset of the browser alignment engine; it intentionally supplies a starting experiment rather than promising API parity with every lab.

## Storage and sharing

SQLite uses salted scrypt hashes, random session tokens stored hashed, foreign keys and WAL. Server saves use an optimistic version check within a transaction. Projects stay owner-private. Course membership does not grant access to peers' work. Only explicit submissions expose fixed snapshots to the submitting student and owning teacher. Roles are stored server-side; public registration never creates teachers.

## Deliberate extensibility

New lessons, languages, scenarios and repository annotations are JSON additions. New engines implement a common `runLab(name,input,options)` result containing baseline, revision and trace. Upstream adapters belong in a student's new code, while pinned originals remain separate. Optional institutional SSO or model tutoring should be introduced behind explicit service contracts, not as hidden dependencies of the offline learning experience.
