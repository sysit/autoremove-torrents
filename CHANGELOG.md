# Changelog

All notable changes to this project will be documented in this file.

## [1.6.1] - 2026-11-08

### Fixed
- **`remote_free_space` no longer acts on unknown free space** - Transmission
  returns `-1` for a nonexistent path and qBittorrent 3.x returns `None`;
  both previously caused the condition to remove every candidate torrent
  (or crash). It now aborts the strategy with a clear error instead.
- **`remove:` expression precedence** - `and` now binds tighter than `or`
  (standard boolean precedence), matching the documentation.
  Previously `A or B and C` was evaluated as `(A or B) and C`, silently
  producing a different removal set.
- **uTorrent total download speed** - `client_status` summed the upload-speed
  field into the download speed.
- **Category filter works for all clients** - torrents that don't carry a
  category (Transmission < 3.3, qBittorrent v2 list responses without the
  field) used to crash the category filter with an `AttributeError`.
- **Unknown strategy keys are now reported** - a typo such as `ratios:` instead
  of `ratio:` used to be silently ignored (the strategy would remove nothing);
  it now logs a warning.
- **Non-string YAML filter values** (e.g. `categories: [2024]`) no longer
  crash the strategy.
- **Failed runs now exit non-zero**, so cron and other schedulers can detect
  them. `--task` with an unknown name lists the available tasks instead of
  raising a bare `KeyError`.
- **Unknown Deluge torrent states** map to `Unknown` instead of crashing.
- **ZeroDivisionError** in `upload_ratio` for zero-size torrents (magnets
  before metadata) - they are kept instead.
- **Missing condition settings** (`action`, `min`, `limit`, `path`) now raise
  a clear error instead of a bare `KeyError`; unknown sort `action` values
  are rejected instead of being silently ignored.
- **`Torrent.__str__` no longer crashes** on torrents missing optional fields
  (e.g. uTorrent provides no create/seeding time); it prints `(Not Provided)`.
- All WebUI requests now use a 30-second timeout, so a stalled client can no
  longer hang an unattended run forever.

### Changed
- **Python 3 only** - removed the Python 2 compatibility layer
  (`autoremovetorrents/compatibility/`); dropped `enum34` and `psutil`
  dependencies.
- Clients expose a single `get_all_torrents()` call. Transmission now fetches
  all torrents in one RPC instead of two requests per torrent; the per-hash
  caches (and their stale-cache races) are gone.
- **`content_paths` filter is now documented** in the configuration reference
  (docs/config.rst), including the note that only qBittorrent and Transmission
  report the download directory.
- PLY generated tables (`lextab.py`/`parsetab.py`) are no longer tracked in
  git; they are rebuilt automatically at import time.
- Test suites are parametrized per case file, so each case is an independent
  test (a failure no longer masks the remaining cases).
- Removed committed scratch files `test_content_path.py` and `test_config.yml`
  (**the latter contained live credentials - rotate that Transmission
  password if it is still in use**).

## [1.6.0] - 2026-03-26

### Added
- **content_path filter** - Filter torrents by their download directory
  - Filter by exact path match
  - Filter by parent directory (e.g., `/downloads/tv` matches `/downloads/tv/show`)
  - Support multiple content paths with `content_paths`
  - Support exclusion with `excluded_content_paths`
  - Works with qBittorrent and Transmission clients

### Example
```yaml
strategies:
  movies_cleanup:
    content_paths:
      - /downloads/movies
    remove: seeding_time > 2592000 or ratio > 2

  tv_cleanup:
    content_paths:
      - /downloads/tv
    excluded_content_paths:
      - /downloads/tv/important
    remove: seeding_time > 1209600
```

## [1.5.5] - 2024-04-27

### Fixed
- Fix broken `delete_torrents` on qBittorrent 4.5.0+
- Documentation updates

## [1.5.4] - 2022-06-19

### Fixed
- Various bug fixes

## [1.5.3] - 2021-01-21

### Fixed
- Various bug fixes