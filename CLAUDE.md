# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python scripts for DaVinci Resolve with two main feature sets:

1. **EXIF Frame Scripts**: Add decorative frames with EXIF metadata to images
2. **Broadcast Format Scripts**: Apply broadcast format presets to project settings

**Platform Support**: Cross-platform (macOS and Windows)

## Architecture

### EXIF Frame Scripts

Two versions exist to support different DaVinci Resolve editions:

- **Studio version** ([add_exif_frame_dv.py](scripts/add_exif_frame_dv.py)): Full UI with customizable options (border color, size, text overrides). Requires DaVinci Resolve Studio's Fusion API.
- **Free version** ([add_exif_frame_dv_lite.py](scripts/add_exif_frame_dv_lite.py)): Simplified version with fixed white border and Polaroid-style layout. No UI dialogs required.

### Broadcast Format Scripts

- **Studio version** ([set_broadcast_format_dv.py](scripts/set_broadcast_format_dv.py)): Apply broadcast format presets (HD, 4K UHD, DCI 4K) to project settings. Features UI for preset selection, custom preset creation, and saving current settings.
- **Debug utility** ([debug_project_settings.py](scripts/debug_project_settings.py)): Dumps all available project settings to a JSON file for investigating setting keys.

### Core Components

**EXIF Frame Scripts** share the same underlying logic:

1. **EXIF extraction**: Dual-path approach handles both standard image formats (JPEG/PNG/TIFF via Pillow) and RAW formats (ARW/CR2/CR3/NEF/DNG/RAF/ORF via rawpy + exifread)
2. **Image processing**: Generates bordered composite with configurable margins and Polaroid-style bottom border
3. **Text rendering**: Automatically formats camera name, lens model, and shooting parameters (focal length, aperture, shutter speed, ISO)
4. **DaVinci Resolve integration**: Operates on timeline clips under the playhead, replacing them with framed versions

**Broadcast Format Scripts**:

1. **Preset management**: Load built-in presets from JSON ([presets/broadcast_presets.json](presets/broadcast_presets.json)) and custom presets from user directory
2. **Settings application**: Apply presets using `project.SetSetting()` API
3. **Custom preset storage**: Save current project settings as reusable presets in user's application support directory

### Key Technical Details

- **Cross-platform installer**: Python-based installer ([scripts/install.py](scripts/install.py)) automatically detects platform (macOS/Windows) and uses appropriate installation paths
- **Dynamic library path detection**: Scripts detect site-packages location via (1) environment variable `DAVINCI_RESOLVE_SCRIPTS_VENV`, or (2) path embedded during installation. The installer automatically detects and embeds the current project's `.venv` path during installation.
- **Font fallback system**: Attempts macOS system fonts (SFNS) before falling back to Arial
- **EXIF tag normalization**: Handles vendor-specific tag names and ratio conversions for camera metadata
- **Output naming**: Appends `_framed` to original filename; skips files already containing this suffix

## Development Commands

### Environment Setup
```bash
# Install dependencies using uv (Python 3.11+)
uv sync
```

### Installation to DaVinci Resolve

**macOS/Linux** (using Makefile):
```bash
# Check environment (Python, libraries, install directory)
make check

# Interactive install (prompts for Free or Studio version)
make install

# Uninstall all scripts
make uninstall
```

**Windows** (or direct Python usage):
```bash
# Check environment
python scripts/install.py check

# Interactive install
python scripts/install.py install

# Uninstall all scripts
python scripts/install.py uninstall
```

**Installation Paths**:
- **macOS**: `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility`
- **Windows**: `%APPDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility`

**Available Scripts**:
1. EXIF Frame - Free version
2. EXIF Frame - Studio version
3. Broadcast Format - Studio version (includes preset file installation)
4. Debug - Project Settings Dumper

### Linting and Formatting
```bash
# Run linter
make lint

# Run formatter
make format

# Auto-fix issues (lint + format)
make fix
```

## Important Constraints

- Scripts must run inside DaVinci Resolve's Python environment (global `resolve` object required)
- **EXIF Frame scripts**: Dependencies (Pillow, rawpy, exifread) must be installed to a virtual environment; the path is automatically embedded during installation
- **Broadcast Format scripts**: No external dependencies required (uses only DaVinci Resolve API)
- Studio version scripts rely on Fusion's UIManager for dialog rendering
- Free version scripts intentionally have no UI to avoid Fusion API dependencies

## Testing Approach

No automated tests exist. Manual testing workflow:

1. Install script via `make install` (macOS/Linux) or `python scripts/install.py install` (Windows)
2. Restart DaVinci Resolve
3. Place timeline playhead over a clip
4. Run script from Workspace > Scripts > Utility menu
5. Verify framed output appears in media pool or replaces timeline clip
