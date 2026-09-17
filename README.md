# DIKWP OpenStudio — China–ASEAN Edition

**Learn a method. Choose with reasons. Experiment. Inherit with provenance. Create your own contribution.**

Created for Yucong Duan's (段玉聪) Guangxi AI Institute lecture and China–ASEAN learning context. Version 1.0.0, 16 September 2026. Apache-2.0 for new platform code and new teaching content.

[中文完整说明](README_CN.md) · [Offline studio](OpenStudio_Offline.html) · [Language coverage](docs/LANGUAGE_COVERAGE.md) · [Architecture](docs/ARCHITECTURE.md) · [Inheritance](docs/UPSTREAM_INHERITANCE.md)

## Working features

- 12 complete Chinese, English and Vietnamese modules, worked examples, misconceptions, exercises, self-checks, prerequisites and repository bridges.
- 13-language main navigation, common controls, core terminology and a multilingual concept-query dictionary. Extended explanations and original research records have the coverage documented separately.
- 483 provenance-tagged candidate entries; 48 curated starting points; explainable problem-fit retrieval, filtering and up-to-six-component comparison.
- Four editable deterministic labs: structured semantic alignment, interval-based 3-No analysis, purpose/action checking, and purpose-aware semantic routing. Inputs, baselines, revisions and computation traces can be exported and replayed.
- A D/I/K/W/P project studio with inheritance/change statements, hypotheses and reflections, JSON export, and a runnable Python scaffold ZIP with tests and upstream-lock manifest.
- Optional standard-library Python WSGI + SQLite accounts, private versioned projects, teacher-created courses, join codes, explicit submission snapshots and teacher feedback.
- Research library linking the 128-page companion lecture, 107 source entries and ten published-book records.
- Commit pinning, source download, archive inspection and receipt generation without executing remote code; optional paginated catalogue metadata refresh.

## Get the source

```bash
git clone https://github.com/YucongDuan/ASEAN_DIKWP_OpenStudio_v1.0.0.git
cd ASEAN_DIKWP_OpenStudio_v1.0.0
```

## Run

Open `OpenStudio_Offline.html` locally for learning and experiments without accounts, network access or a model key. Save project exports to carry your work across devices. If the browser refuses local storage, the app reports it rather than claiming a successful save.

For local accounts and courses, Python 3.10+ is sufficient:

```bash
python server.py
# http://127.0.0.1:8765
python server.py create-teacher --username teacher
```

The teacher command prompts for a password. Web registration always creates students. There are no default credentials. The bundled server is loopback-only; use the WSGI entry point and institution-managed HTTPS for a shared deployment.

Run the included exported student project:

```bash
cd examples/cross_language_trade
python experiment.py
python -m unittest discover -s tests -v
```

The exported code is a new teaching scaffold, not bundled or automatically integrated upstream code. The upstream tool helps you retrieve precise source revisions and retain license/provenance records before implementing adapters.

## Source layout

`web/` contains a dependency-free browser app and teaching core. `app/` contains the WSGI application, authentication, project history and course services. `data/` contains editable learning, locale, scenario, catalogue and source JSON. `scripts/` builds the offline edition and handles upstream metadata/source preparation. `examples/` contains a runnable student export. `tests/` and `qa/` contain actual regression checks and their scope.

## Build and test

```bash
python scripts/build_content.py
python scripts/add_vietnamese.py
python scripts/build_locales.py
python scripts/build_web.py
python -m unittest discover -s tests -p 'test_*.py' -v
node tests/test_core.js
```

Building content reconstructs the seed dataset and can overwrite edits; maintain changes in the builders or keep a backup. `build_web.py` alone repackages edited JSON without recreating it. Node is required only for development tests, not end-user operation. Browser checks use a documented test harness; see `qa/RELEASE_CHECKS.md`.

## Provenance, participation and scope

The catalogue is a dated, inherited research-navigation dataset, not evidence that every repository has been installed or evaluated. Problem-fit scores do not rank scientific merit. The four labs are deliberately small teaching implementations, not hidden calls to PACT or other upstream products. Deep lessons are complete in Chinese, English and Vietnamese; original publications retain their original languages. Translations are open for community review.

Research foundations and selected upstream works are credited to Yucong Duan. The initial platform implementation and new teaching materials were AI-assisted. Original papers, books, websites and upstream code retain their own licenses; this repository's license does not replace theirs. Source code is published in the [official GitHub repository](https://github.com/YucongDuan/ASEAN_DIKWP_OpenStudio_v1.0.0). Institutional hosting is configured separately; see the deployment guide.
