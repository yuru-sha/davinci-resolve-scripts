# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python scripts for DaVinci Resolve that add decorative frames with EXIF metadata to images. The scripts extract camera settings from photos and RAW files, then generate Polaroid-style frames with the metadata embedded.

## Architecture

### Script Variants

Two versions exist to support different DaVinci Resolve editions:

- **Studio version** ([add_exif_frame_dv.py](scripts/add_exif_frame_dv.py)): Full UI with customizable options (border color, size, text overrides). Requires DaVinci Resolve Studio's Fusion API.
- **Free version** ([add_exif_frame_dv_lite.py](scripts/add_exif_frame_dv_lite.py)): Simplified version with fixed white border and Polaroid-style layout. No UI dialogs required.

### Core Components

Both scripts share the same underlying logic:

1. **EXIF extraction**: Dual-path approach handles both standard image formats (JPEG/PNG/TIFF via Pillow) and RAW formats (ARW/CR2/CR3/NEF/DNG/RAF/ORF via rawpy + exifread)
2. **Image processing**: Generates bordered composite with configurable margins and Polaroid-style bottom border
3. **Text rendering**: Automatically formats camera name, lens model, and shooting parameters (focal length, aperture, shutter speed, ISO)
4. **DaVinci Resolve integration**: Operates on timeline clips under the playhead, replacing them with framed versions

### Key Technical Details

- **Dynamic library path detection**: Scripts detect site-packages location via (1) environment variable `DAVINCI_RESOLVE_SCRIPTS_VENV`, or (2) path embedded during installation by `make install`. The Makefile automatically detects and embeds the current project's `.venv` path during installation.
- **Font fallback system**: Attempts macOS system fonts (SFNS) before falling back to Arial
- **EXIF tag normalization**: Handles vendor-specific tag names and ratio conversions for camera metadata
- **Output naming**: Appends `_framed` to original filename; skips files already containing this suffix

## Development Commands

### Environment Setup
```bash
# Install dependencies using uv (Python 3.13+)
uv sync
```

### Installation to DaVinci Resolve
```bash
# Check environment (Python, libraries, install directory)
make check

# Interactive install (prompts for Free or Studio version)
make install

# Uninstall all scripts
make uninstall
```

Scripts install to: `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility`

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
- Dependencies (Pillow, rawpy, exifread) must be installed to a virtual environment; the path is automatically embedded during `make install`
- Studio version relies on Fusion's UIManager for dialog rendering
- Free version intentionally has no configurable options to avoid Fusion API dependencies

## Testing Approach

No automated tests exist. Manual testing workflow:

1. Install script via `make install`
2. Restart DaVinci Resolve
3. Place timeline playhead over a clip
4. Run script from Workspace > Scripts > Utility menu
5. Verify framed output appears in media pool or replaces timeline clip
