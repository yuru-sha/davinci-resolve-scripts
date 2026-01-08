#!/usr/bin/env python3
"""
Set Broadcast Format for DaVinci Resolve (Studio Version)

This script allows you to apply broadcast format presets to your DaVinci Resolve project.
It provides a UI dialog for selecting presets and can save/load custom presets.

Requirements:
    - DaVinci Resolve Studio (for UI dialogs)
    - Project must be open

Usage:
    Run from Workspace > Scripts > Utility > set_broadcast_format_dv

Features:
    - Apply built-in broadcast format presets
    - Save current settings as custom presets
    - Load and apply custom presets
    - View current project settings

Author: Generated for yuru-sha/davinci-resolve-scripts
"""

import os
import sys
import json
from pathlib import Path


# ===== Configuration =====

def get_preset_paths():
    """Get paths for default and custom preset files."""
    # Default presets (bundled with script)
    script_dir = Path(__file__).parent
    default_presets = script_dir.parent / "presets" / "broadcast_presets.json"

    # Custom presets directory
    home = Path.home()
    if sys.platform == "darwin":
        custom_dir = home / "Library" / "Application Support" / "DaVinci Resolve Custom Presets"
    elif sys.platform == "win32":
        appdata = os.environ.get("APPDATA", str(home / "AppData" / "Roaming"))
        custom_dir = Path(appdata) / "DaVinci Resolve Custom Presets"
    else:
        custom_dir = home / ".config" / "DaVinci Resolve Custom Presets"

    # Ensure custom directory exists
    custom_dir.mkdir(parents=True, exist_ok=True)

    custom_presets = custom_dir / "custom_presets.json"

    return default_presets, custom_presets


def load_presets():
    """Load both default and custom presets."""
    default_path, custom_path = get_preset_paths()

    all_presets = {}

    # Load default presets
    if default_path.exists():
        try:
            with open(default_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "presets" in data:
                    all_presets.update(data["presets"])
        except Exception as e:
            print(f"Warning: Failed to load default presets: {e}")

    # Load custom presets
    if custom_path.exists():
        try:
            with open(custom_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "presets" in data:
                    # Prefix custom presets with "[Custom]"
                    for name, preset in data["presets"].items():
                        all_presets[f"[Custom] {name}"] = preset
        except Exception as e:
            print(f"Warning: Failed to load custom presets: {e}")

    return all_presets


def save_custom_preset(name, settings, description=""):
    """Save a custom preset."""
    _, custom_path = get_preset_paths()

    # Load existing custom presets
    existing_presets = {}
    if custom_path.exists():
        try:
            with open(custom_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "presets" in data:
                    existing_presets = data["presets"]
        except Exception:
            pass

    # Add new preset
    existing_presets[name] = {
        "description": description,
        "settings": settings
    }

    # Save back to file
    output_data = {
        "_description": "Custom broadcast format presets",
        "presets": existing_presets
    }

    try:
        with open(custom_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving custom preset: {e}")
        return False


def get_current_settings(project):
    """Get current project settings as a dictionary."""
    try:
        all_settings = project.GetSetting()
        return all_settings if all_settings else {}
    except Exception as e:
        print(f"Error getting current settings: {e}")
        return {}


def apply_preset_settings(project, settings):
    """Apply preset settings to the project."""
    success_count = 0
    failed_settings = []

    for key, value in settings.items():
        try:
            result = project.SetSetting(key, str(value))
            if result:
                success_count += 1
            else:
                failed_settings.append(f"{key} = {value}")
        except Exception as e:
            failed_settings.append(f"{key} = {value} (Error: {e})")

    return success_count, failed_settings


def show_error_dialog(ui, dispatcher, message, title="Error"):
    """Show an error dialog."""
    dialog = dispatcher.AddWindow({
        "WindowTitle": title,
        "ID": "ErrorDialog",
        "Geometry": [100, 100, 500, 150],
    }, [
        ui.VGroup([
            ui.Label({"Text": message, "Alignment": {"AlignHCenter": True}, "WordWrap": True}),
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


def show_success_dialog(ui, dispatcher, message, title="Success"):
    """Show a success dialog."""
    show_error_dialog(ui, dispatcher, message, title)


def show_preset_selector(ui, dispatcher, presets):
    """Show preset selection dialog."""
    preset_names = sorted(presets.keys())

    dialog = dispatcher.AddWindow({
        "WindowTitle": "Select Broadcast Format Preset",
        "ID": "PresetSelectorDialog",
        "Geometry": [100, 100, 600, 500],
    }, [
        ui.VGroup({"Spacing": 10}, [
            ui.Label({
                "Text": "Choose a broadcast format preset to apply:",
                "Alignment": {"AlignHCenter": True},
                "Font": ui.Font({"PixelSize": 13, "StyleName": "Bold"}),
                "Weight": 0
            }),
            ui.VGroup({"Frame": True, "Weight": 1}, [
                ui.Tree({"ID": "PresetTree", "HeaderHidden": True})
            ]),
            ui.Label({
                "ID": "DescriptionLabel",
                "Text": "Select a preset to see details",
                "Alignment": {"AlignLeft": True},
                "WordWrap": True,
                "Weight": 0
            }),
            ui.HGroup({"Weight": 0}, [
                ui.Button({"ID": "ApplyButton", "Text": "Apply Preset", "Weight": 1}),
                ui.Button({"ID": "SaveCurrentButton", "Text": "Save Current Settings", "Weight": 1}),
                ui.Button({"ID": "CancelButton", "Text": "Cancel", "Weight": 1})
            ])
        ])
    ])

    # Populate preset tree
    tree = dialog.GetItems()["PresetTree"]
    for preset_name in preset_names:
        tree.AddTopLevelItem(tree.NewItem())
        item = tree.TopLevelItem(tree.TopLevelItemCount() - 1)
        item.Text[0] = preset_name

    selected_preset = None

    def on_tree_selection_changed(ev):
        items = dialog.GetItems()
        tree = items["PresetTree"]
        current_item = tree.CurrentItem()
        if current_item:
            preset_name = current_item.Text[0]
            preset = presets.get(preset_name, {})
            description = preset.get("description", "No description available")
            settings = preset.get("settings", {})

            # Format settings display
            settings_str = "\n".join([f"  {k}: {v}" for k, v in settings.items()])
            full_text = f"{description}\n\nSettings:\n{settings_str}"

            items["DescriptionLabel"].Text = full_text

    def on_apply_clicked(ev):
        nonlocal selected_preset
        items = dialog.GetItems()
        tree = items["PresetTree"]
        current_item = tree.CurrentItem()
        if current_item:
            selected_preset = current_item.Text[0]
        dispatcher.ExitLoop()

    def on_save_current_clicked(ev):
        nonlocal selected_preset
        selected_preset = "__SAVE_CURRENT__"
        dispatcher.ExitLoop()

    def on_cancel_clicked(ev):
        dispatcher.ExitLoop()

    def on_close(ev):
        dispatcher.ExitLoop()

    dialog.On.PresetTree.ItemSelectionChanged = on_tree_selection_changed
    dialog.On.ApplyButton.Clicked = on_apply_clicked
    dialog.On.SaveCurrentButton.Clicked = on_save_current_clicked
    dialog.On.CancelButton.Clicked = on_cancel_clicked
    dialog.On.PresetSelectorDialog.Close = on_close

    dialog.Show()
    dispatcher.RunLoop()
    dialog.Hide()

    return selected_preset


def show_save_preset_dialog(ui, dispatcher):
    """Show dialog to save current settings as a custom preset."""
    dialog = dispatcher.AddWindow({
        "WindowTitle": "Save Custom Preset",
        "ID": "SavePresetDialog",
        "Geometry": [100, 100, 450, 200],
    }, [
        ui.VGroup({"Spacing": 10}, [
            ui.Label({"Text": "Save current project settings as a custom preset:", "Weight": 0}),
            ui.VGroup({"Frame": True, "Weight": 1}, [
                ui.HGroup([
                    ui.Label({"Text": "Preset Name:", "Weight": 0}),
                    ui.LineEdit({"ID": "PresetNameInput", "PlaceholderText": "Enter preset name", "Weight": 1})
                ]),
                ui.HGroup([
                    ui.Label({"Text": "Description:", "Weight": 0}),
                    ui.LineEdit({"ID": "DescriptionInput", "PlaceholderText": "Optional description", "Weight": 1})
                ])
            ]),
            ui.HGroup({"Weight": 0}, [
                ui.Button({"ID": "SaveButton", "Text": "Save", "Weight": 1}),
                ui.Button({"ID": "CancelButton", "Text": "Cancel", "Weight": 1})
            ])
        ])
    ])

    result = None

    def on_save_clicked(ev):
        nonlocal result
        items = dialog.GetItems()
        preset_name = items["PresetNameInput"].Text.strip()
        description = items["DescriptionInput"].Text.strip()

        if not preset_name:
            show_error_dialog(ui, dispatcher, "Preset name cannot be empty!")
            return

        result = {
            "name": preset_name,
            "description": description
        }
        dispatcher.ExitLoop()

    def on_cancel_clicked(ev):
        dispatcher.ExitLoop()

    def on_close(ev):
        dispatcher.ExitLoop()

    dialog.On.SaveButton.Clicked = on_save_clicked
    dialog.On.CancelButton.Clicked = on_cancel_clicked
    dialog.On.SavePresetDialog.Close = on_close

    dialog.Show()
    dispatcher.RunLoop()
    dialog.Hide()

    return result


def main():
    """Main entry point."""
    # Check if running in DaVinci Resolve
    try:
        resolve_obj = resolve  # noqa: F821 - global object provided by DaVinci Resolve
    except NameError:
        print("Error: This script must be run inside DaVinci Resolve.")
        sys.exit(1)

    # Get current project
    project_manager = resolve_obj.GetProjectManager()
    project = project_manager.GetCurrentProject()

    if not project:
        print("Error: No project is currently open.")
        return

    # Initialize Fusion UI
    try:
        fusion = resolve_obj.Fusion()
        ui = fusion.UIManager()
        dispatcher = bmd.UIDispatcher(ui)  # noqa: F821 - global object provided by DaVinci Resolve
    except Exception as e:
        print(f"Error: Failed to initialize UI. This script requires DaVinci Resolve Studio.\n{e}")
        return

    # Load presets
    presets = load_presets()

    if not presets:
        show_error_dialog(
            ui, dispatcher,
            "No presets found!\n\nPlease ensure broadcast_presets.json exists in the presets/ directory."
        )
        return

    # Show preset selector
    selected_preset_name = show_preset_selector(ui, dispatcher, presets)

    if not selected_preset_name:
        return  # User cancelled

    # Handle "Save Current Settings" action
    if selected_preset_name == "__SAVE_CURRENT__":
        save_info = show_save_preset_dialog(ui, dispatcher)
        if not save_info:
            return  # User cancelled

        current_settings = get_current_settings(project)
        if not current_settings:
            show_error_dialog(
                ui, dispatcher,
                "Failed to retrieve current project settings."
            )
            return

        success = save_custom_preset(
            save_info["name"],
            current_settings,
            save_info["description"]
        )

        if success:
            show_success_dialog(
                ui, dispatcher,
                f"Custom preset '{save_info['name']}' saved successfully!"
            )
        else:
            show_error_dialog(
                ui, dispatcher,
                "Failed to save custom preset. Check console for details."
            )
        return

    # Apply selected preset
    preset = presets.get(selected_preset_name)
    if not preset:
        show_error_dialog(ui, dispatcher, f"Preset '{selected_preset_name}' not found!")
        return

    settings_to_apply = preset.get("settings", {})
    if not settings_to_apply:
        show_error_dialog(ui, dispatcher, "Selected preset has no settings defined!")
        return

    # Apply settings
    success_count, failed_settings = apply_preset_settings(project, settings_to_apply)

    # Show result
    if failed_settings:
        failed_str = "\n".join(failed_settings)
        message = f"Applied {success_count}/{len(settings_to_apply)} settings.\n\nFailed settings:\n{failed_str}"
        show_error_dialog(ui, dispatcher, message, "Partial Success")
    else:
        message = f"Successfully applied all {success_count} settings from preset:\n'{selected_preset_name}'"
        show_success_dialog(ui, dispatcher, message)


if __name__ == "__main__":
    main()
