# Changelog

All notable changes to this project will be documented in this file.

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