# Inherit real repositories without losing their identity

## From selection to exact source

Selecting a project in the browser creates a source relationship, not an installed dependency. Export a project ZIP and unpack it, for example to `my-project/` alongside the platform. Keep the generated `upstream.lock.json`.

Run from the **platform root**, adjusting paths to your exported project:

```bash
python scripts/upstream.py pin --manifest my-project/upstream.lock.json
python scripts/upstream.py fetch --manifest my-project/upstream.lock.json --dest my-project/vendor
```

`pin` reads the GitHub repository metadata and resolves the default branch to a full commit SHA. `fetch` requests a ZIP for that immutable SHA, extracts it to its own directory and writes an adjacent receipt. It does not install packages, invoke Git hooks or execute downloaded code. GitHub may require a token because of rate limits; the optional `GITHUB_TOKEN` environment variable is used only for api.github.com and removed on cross-host redirects.

The tools allow only HTTPS requests to approved GitHub hosts, at most six selected repositories, 64 MB archives, 256 MB expanded content and 10,000 files. They reject traversal, symlinks, special files, duplicate paths and unreasonable compression. They refuse to overwrite an existing source directory. Large research archives may need a deliberately reviewed alternative workflow rather than increasing every limit blindly.

## Local source archives

If you downloaded a repository ZIP yourself, inspect and extract it without running code:

```bash
python scripts/upstream.py inspect-local --archive downloaded.zip --dest my-project/vendor/manual-source
```

This checks the archive but does not invent a commit relationship for an unlabelled file. Record the download origin and actual commit separately when available.

## Read before adapting

Read the pinned LICENSE/NOTICE and README, identify accepted inputs and returned outputs, and run the original documented reproduction command in an appropriate local environment. Keep the upstream directory unchanged and put transformations in your new adapter. Record why the component was selected and which part is actually used.

For PACT, the README checked for this delivery documents `python scripts/reproduce.py`, Python 3.10+, 72 synthetic scenarios and four deterministic baselines. These are upstream statements, not results rerun by OpenStudio in this delivery. PACT's code license and benchmark-data license differ; preserve both when using them.

The offline delivery does not bundle PACT, MESH², VerityWeave or the other 480 source trees. The built-in lab and exported Python program remain separately identified new educational implementations. Their role is to help learners design and test an adapter, not to claim that unrelated upstream APIs have already been integrated.

## Update the catalogue

```bash
python scripts/sync_catalog.py
# Or import a previously saved complete GitHub REST metadata array:
python scripts/sync_catalog.py --from-json repositories.json
```

The network mode follows pages until completion and refuses partial writes on failure. Existing teaching annotations are preserved; new records are marked metadata-only. Entries absent from the latest response are retained as historical with a flag rather than silently erased. A previous JSON backup is written before replacing the catalogue.

The fetch, pin and sync code paths have deterministic transport-double tests; this release's container could not complete live GitHub downloads. Do not treat the test receipts as real upstream download receipts. Run the real commands on a network-enabled machine and retain the generated receipts.
