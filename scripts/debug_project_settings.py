#!/usr/bin/env python3
"""
Debug script to dump all available DaVinci Resolve project settings.

This script retrieves and displays all available project settings from DaVinci Resolve,
which is useful for identifying the correct setting keys needed for automation scripts.

Usage:
    1. Install this script to DaVinci Resolve Scripts directory
    2. Run from Workspace > Scripts > Utility > debug_project_settings
    3. Check output file or console for available settings

Output:
    Creates a file in user's home directory with all project settings
"""

import os
import sys
import json
from datetime import datetime


def get_output_path():
    """Get platform-specific output file path."""
    home = os.path.expanduser("~")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resolve_project_settings_{timestamp}.json"

    if sys.platform == "darwin":
        # macOS: Use Desktop
        return os.path.join(home, "Desktop", filename)
    elif sys.platform == "win32":
        # Windows: Use Desktop
        return os.path.join(home, "Desktop", filename)
    else:
        # Linux/Other: Use home directory
        return os.path.join(home, filename)


def dump_project_settings():
    """Dump all project settings to a JSON file."""
    try:
        # Get current project
        resolve_obj = resolve  # noqa: F821 - global object provided by DaVinci Resolve
        project_manager = resolve_obj.GetProjectManager()
        project = project_manager.GetCurrentProject()

        if not project:
            return {
                "error": "No project is currently open",
                "instructions": "Please open a project in DaVinci Resolve and run this script again"
            }

        # Get project information
        project_name = project.GetName()

        # Get all project settings (no arguments returns dict of all settings)
        all_settings = project.GetSetting()

        # Get current timeline information if available
        timeline_info = {}
        current_timeline = project.GetCurrentTimeline()
        if current_timeline:
            timeline_info = {
                "name": current_timeline.GetName(),
                "start_frame": current_timeline.GetStartFrame(),
                "end_frame": current_timeline.GetEndFrame(),
            }
            # Try to get timeline-specific settings
            try:
                timeline_settings = current_timeline.GetSetting()
                timeline_info["settings"] = timeline_settings
            except Exception as e:
                timeline_info["settings_error"] = str(e)

        # Compile all information
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "project_name": project_name,
            "project_settings": all_settings,
            "timeline_info": timeline_info,
            "notes": {
                "usage": "Use these setting keys with project.SetSetting(key, value)",
                "example": "project.SetSetting('timelineFrameRate', '23.976')"
            }
        }

        return output_data

    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__,
            "instructions": "Make sure you're running this script inside DaVinci Resolve"
        }


def main():
    """Main entry point."""
    # Dump settings
    settings_data = dump_project_settings()

    # Write to file
    output_path = get_output_path()

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, indent=2, ensure_ascii=False)

        message = f"Project settings dumped successfully!\n\nOutput file: {output_path}"
        print(message)

        # Try to show dialog in DaVinci Resolve Studio
        try:
            fusion = resolve.Fusion()  # noqa: F821
            ui = fusion.UIManager()
            dispatcher = bmd.UIDispatcher(ui)  # noqa: F821

            dialog = dispatcher.AddWindow({
                "WindowTitle": "Project Settings Dumped",
                "ID": "DebugSettingsDialog",
                "Geometry": [100, 100, 500, 150],
            }, [
                ui.VGroup([
                    ui.Label({"Text": "Project settings have been saved!", "Alignment": {"AlignHCenter": True}}),
                    ui.Label({"Text": output_path, "Alignment": {"AlignHCenter": True}, "WordWrap": True}),
                    ui.Button({"ID": "OkButton", "Text": "OK"}),
                ]),
            ])

            def on_close(ev):
                dispatcher.ExitLoop()

            dialog.On.OkButton.Clicked = on_close
            dialog.On.DebugSettingsDialog.Close = on_close

            dialog.Show()
            dispatcher.RunLoop()
            dialog.Hide()

        except Exception:
            # If UI fails (Free version or error), just print to console
            pass

    except Exception as e:
        error_message = f"Failed to write output file: {e}"
        print(error_message)

        # Try to show error dialog
        try:
            fusion = resolve.Fusion()  # noqa: F821
            ui = fusion.UIManager()
            dispatcher = bmd.UIDispatcher(ui)  # noqa: F821

            dialog = dispatcher.AddWindow({
                "WindowTitle": "Error",
                "ID": "ErrorDialog",
                "Geometry": [100, 100, 400, 120],
            }, [
                ui.VGroup([
                    ui.Label({"Text": error_message, "Alignment": {"AlignHCenter": True}, "WordWrap": True}),
                    ui.Button({"ID": "OkButton", "Text": "OK"}),
                ]),
            ])

            def on_close(ev):
                dispatcher.ExitLoop()

            dialog.On.OkButton.Clicked = on_close
            dialog.On.ErrorDialog.Close = on_close

            dialog.Show()
            dispatcher.RunLoop()
            dialog.Hide()

        except Exception:
            pass


if __name__ == "__main__":
    main()
