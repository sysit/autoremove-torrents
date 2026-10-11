# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

`autoremove-torrents` — a Python CLI that connects to torrent clients (qBittorrent, Transmission, µTorrent, Deluge) via their WebUI APIs and removes torrents according to user-defined strategies in a YAML config file. Entry point: `autoremovetorrents/main.py` (console script `autoremove-torrents`).

## Commands

```bash
# Install (package is installed via setup.py; a local venv/ exists)
python setup.py install          # or: pip install -e .

# Run all tests (CI command; run from repo root)
py.test -s --cov --log-level=INFO

# Run one test file / one test
pytest pytest/test_strategies/test_strategies.py
pytest pytest/test_strategies/test_strategies.py -k ratio

# Lint (CI blocks on syntax errors and undefined names)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

- Tests live in the `pytest/` **directory** (not a config file). Each subdir's `conftest.py` appends the repo root to `sys.path`.
- `pytest/test_strategies/` and `pytest/test_main/` are offline (JSON fixtures / `requests_mock`).
- `pytest/test_clients/` is an **integration suite**: it reads YAML cases from `pytest/test_clients/cases/` and connects to real client instances addressed via env vars (`DELUGE_*`, `QBITTORRENT_*`, `TRANSMISSION_*`, `UTORRENT_*`). CI (`.github/workflows/build.yml`) spins the clients up as service containers; without them these tests fail. Set `QBITTORRENT_4_HOST`/etc. to skip-free-run against your own instances.

## Architecture

Flow: `main.py` → one `Task` per top-level key in the YAML config → `Strategy` → filters → conditions → removal.

- **`task.py` (`Task`)** — orchestrates one config task: substitutes `$(ENV_VAR)` in `host`/`username`/`password`, instantiates the client from a name→class map, fetches *all* torrents into a set of `Torrent` objects, applies each strategy, merges removal sets, deletes via `client.remove_torrents()`. `force_delete` config key exists for CI testing only.
- **`client/`** — one adapter per client (`qbittorrent.py`, `transmission.py`, `utorrent.py`, `deluge.py`). Each normalizes its WebUI API into the same interface: `login()`, `version()`, `api_version()`, `client_status()`, `get_all_torrents() -> set[Torrent]`, `remove_torrents(hashes, delete_data)`, plus `remote_free_space(path)` (exposed via `ClientStatus.free_space`). Client quirks (API versions, field names) are confined here — e.g. qBittorrent ≥4.5 login handling, and `12335fc` fixed deletion on qbt 4.5.0+. All HTTP goes through `httpsession.HttpSession` (30s default timeout).
- **`torrent.py` (`Torrent`)** — plain attribute bag populated by client adapters (`hash`, `name`, `category`, `tracker`, `status`, `ratio`, `seeding_time`, `content_path`, …). Note: `last_activity` holds a *time interval*, not a unix timestamp.
- **`strategy.py` (`Strategy`)** — a pipeline. First `_apply_filters()` narrows the candidate set (category, status, tracker, content_path; each with accept/exclude lists). Then `_apply_conditions()` removes from what remains, using the fixed `conditions` dict mapping YAML keys (`ratio`, `seeding_time`, `max_progress`, …) to condition classes.
- **`condition/`** — each condition class extends `condition/base.py::Condition`, which splits the torrent set into `remain`/`remove` via `Comparer` (LT/GT/EQ). `freespacebase.py` is shared by free-space conditions; `sortbase.py` implements the `action`-driven ordering. The **single registry** of condition names is `condition/__init__.py` (`YAML_CONDITIONS` for strategy-block keys, `DSL_CONDITIONS` for `remove:` expression names) — both `strategy.py` and `conditionparser.py` consume it; add new conditions there, nowhere else. Unknown strategy keys are logged as warnings in `strategy.py`.
- **Condition DSL (`remove:` key)** — `strategy.py` maps `remove` to `conditionparser.py`, a PLY grammar (`conditionlexer.py` + `conditionparser.py`) supporting expressions like `ratio > 2.0 && seeding_time > 259200`. Precedence is standard: `and` binds tighter than `or`. `lextab.py`/`parsetab.py` are **generated** — delete them and re-import to regenerate after any grammar/precedence change (PLY's optimize mode does NOT detect precedence-only changes), don't hand-edit.
- **`util/`** — formatters (`convert_bytes`, `convert_seconds`, `convert_speed`, `convert_timestamp`) used by `Torrent.__str__` and clients; `httpsession.py` holds the timeout-injecting requests Session.

## Conventions

- Version lives in `autoremovetorrents/version.py`; user-facing changes go in `CHANGELOG.md`. Docs (`docs/`) are Sphinx and document the config format — new filters/conditions need entries there and in both READMEs (`README.rst`, `README-cn.rst`).
- Adding a new condition means: new class in `condition/`, an entry in `YAML_CONDITIONS` (and `DSL_CONDITIONS` if DSL-exposed) in `condition/__init__.py`, plus tests in `pytest/test_strategies/`.
- Codebase is Python 3 only (the Python 2 `compatibility/` layer was removed): `open(..., encoding=...)`, `urllib.parse`, `shutil.disk_usage`, `math.inf` are used directly. Style: `#-*- coding:utf-8 -*-` headers, `logger.Logger.register(__name__)` for logging.
