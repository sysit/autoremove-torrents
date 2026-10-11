# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed
- **`remove:` expression precedence** - `and` now binds tighter than `or`
  (standard boolean precedence), matching the documentation.
  Previously `A or B and C` was evaluated as `(A or B) and C`, silently
  producing a different removal set.
- **uTorrent total download speed** - `client_status` summed the upload-speed
  field into the download speed.
- **Unknown strategy keys are now reported** - a typo such as `ratios:` instead
  of `ratio:` used to be silently ignored (the strategy would remove nothing);
  it now logs a warning.
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