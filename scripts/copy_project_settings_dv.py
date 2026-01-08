#!/usr/bin/env python3
"""
Copy Project Settings (Studio Version)

This script copies all settings from an existing project to a new project in DaVinci Resolve.
Studio version uses Fusion UI dialogs for interactive operation.

Usage:
    Run this script from DaVinci Resolve Studio: Workspace > Scripts > Utility > Copy Project Settings
"""

import sys


def show_error_dialog(ui, dispatcher, message):
    """Show error dialog."""
    win = dispatcher.AddWindow(
        {"ID": "ErrorWin", "Geometry": [500, 300, 400, 150], "WindowTitle": "Error"},
        [
            ui.VGroup(
                {"Spacing": 10},
                [
                    ui.Label(
                        {
                            "Text": message,
                            "Weight": 1,
                            "WordWrap": True,
                            "Alignment": {"AlignHCenter": True, "AlignVCenter": True},
                        }
                    ),
                    ui.Button({"ID": "OK", "Text": "OK", "Weight": 0}),
                ],
            )
        ],
    )

    def on_close(ev):
        dispatcher.ExitLoop()

    def on_ok(ev):
        dispatcher.ExitLoop()

    win.On.ErrorWin.Close = on_close
    win.On.OK.Clicked = on_ok

    win.Show()
    dispatcher.RunLoop()
    win.Hide()


def show_project_selection_dialog(ui, dispatcher, projects):
    """Show project selection dialog. Returns selected project name or None."""
    win = dispatcher.AddWindow(
        {
            "ID": "SelectWin",
            "Geometry": [500, 300, 450, 400],
            "WindowTitle": "Copy Project Settings (Studio)",
        },
        [
            ui.VGroup(
                {"Spacing": 10},
                [
                    ui.Label(
                        {
                            "Text": "Select source project:",
                            "Weight": 0,
                            "Font": ui.Font({"PixelSize": 12, "StyleName": "Bold"}),
                        }
                    ),
                    ui.Tree({"ID": "ProjectTree", "Weight": 1}),
                    ui.HGroup(
                        {"Weight": 0},
                        [
                            ui.Button({"ID": "Next", "Text": "Next", "Weight": 1}),
                            ui.Button({"ID": "Cancel", "Text": "Cancel", "Weight": 1}),
                        ],
                    ),
                ],
            )
        ],
    )

    # Populate tree with projects
    tree = win.GetItems()["ProjectTree"]
    tree_root = tree.NewItem()
    tree_root.Text[0] = "Projects"
    tree.AddTopLevelItem(tree_root)

    for project_name in projects:
        item = tree.NewItem()
        item.Text[0] = project_name
        tree_root.AddChild(item)

    tree_root.SetExpanded(True)

    selected_name = [None]

    def on_close(ev):
        dispatcher.ExitLoop()

    def on_cancel(ev):
        dispatcher.ExitLoop()

    def on_next(ev):
        current_item = tree.CurrentItem()
        if current_item and current_item.Text[0] != "Projects":
            selected_name[0] = current_item.Text[0]
            dispatcher.ExitLoop()

    win.On.SelectWin.Close = on_close
    win.On.Cancel.Clicked = on_cancel
    win.On.Next.Clicked = on_next

    win.Show()
    dispatcher.RunLoop()
    win.Hide()

    return selected_name[0]


def show_name_input_dialog(ui, dispatcher, source_name, settings_count, default_name):
    """Show new project name input dialog. Returns new project name or None."""
    win = dispatcher.AddWindow(
        {
            "ID": "NameWin",
            "Geometry": [500, 300, 450, 250],
            "WindowTitle": "Copy Project Settings (Studio)",
        },
        [
            ui.VGroup(
                {"Spacing": 10},
                [
                    ui.Label(
                        {
                            "Text": f"Source: {source_name}",
                            "Weight": 0,
                            "Font": ui.Font({"PixelSize": 12, "StyleName": "Bold"}),
                        }
                    ),
                    ui.Label(
                        {"Text": f"Settings: {settings_count} items loaded", "Weight": 0}
                    ),
                    ui.Label({"Text": "", "Weight": 0}),  # Spacer
                    ui.Label({"Text": "New Project Name:", "Weight": 0}),
                    ui.LineEdit(
                        {"ID": "NameInput", "Text": default_name, "PlaceholderText": "Enter project name"}
                    ),
                    ui.HGroup(
                        {"Weight": 0},
                        [
                            ui.Button({"ID": "Create", "Text": "Create", "Weight": 1}),
                            ui.Button({"ID": "Cancel", "Text": "Cancel", "Weight": 1}),
                        ],
                    ),
                ],
            )
        ],
    )

    new_name = [None]

    def on_close(ev):
        dispatcher.ExitLoop()

    def on_cancel(ev):
        dispatcher.ExitLoop()

    def on_create(ev):
        name = win.GetItems()["NameInput"].Text.strip()
        if name:
            new_name[0] = name
            dispatcher.ExitLoop()

    win.On.NameWin.Close = on_close
    win.On.Cancel.Clicked = on_cancel
    win.On.Create.Clicked = on_create

    win.Show()
    dispatcher.RunLoop()
    win.Hide()

    return new_name[0]


def show_result_dialog(ui, dispatcher, project_name, success_count, total_count, failed_keys):
    """Show result dialog."""
    # Build result message
    result_text = f"Project created: {project_name}\n\n"
    result_text += f"Settings applied: {success_count}/{total_count}\n"

    if failed_keys:
        result_text += f"\nFailed to apply {len(failed_keys)} setting(s):\n"
        # Show first 10 failed keys
        for key in failed_keys[:10]:
            result_text += f"  • {key}\n"
        if len(failed_keys) > 10:
            result_text += f"  ... and {len(failed_keys) - 10} more\n"
        result_text += "\nNote: Some settings may be read-only or version-specific."
    else:
        result_text += "\nAll settings applied successfully!"

    win = dispatcher.AddWindow(
        {"ID": "ResultWin", "Geometry": [500, 300, 500, 400], "WindowTitle": "Result"},
        [
            ui.VGroup(
                {"Spacing": 10},
                [
                    ui.TextEdit(
                        {
                            "ID": "ResultText",
                            "Text": result_text,
                            "Weight": 1,
                            "ReadOnly": True,
                            "Font": ui.Font({"Family": "Monospace", "PixelSize": 11}),
                        }
                    ),
                    ui.Button({"ID": "OK", "Text": "OK", "Weight": 0}),
                ],
            )
        ],
    )

    def on_close(ev):
        dispatcher.ExitLoop()

    def on_ok(ev):
        dispatcher.ExitLoop()

    win.On.ResultWin.Close = on_close
    win.On.OK.Clicked = on_ok

    win.Show()
    dispatcher.RunLoop()
    win.Hide()


def main():
    """Main function for copying project settings."""
    # Check if running inside DaVinci Resolve
    try:
        resolve_obj = resolve  # noqa: F821
    except NameError:
        print("ERROR: This script must be run within DaVinci Resolve Studio.")
        sys.exit(1)

    # Get ProjectManager and Fusion UI
    pm = resolve_obj.GetProjectManager()
    if not pm:
        print("ERROR: Failed to get ProjectManager.")
        return

    try:
        fusion = resolve_obj.Fusion()
        ui = fusion.UIManager()
        dispatcher = bmd.UIDispatcher(ui)  # noqa: F821
    except Exception as e:
        print(f"ERROR: Failed to initialize Fusion UI: {e}")
        print("This script requires DaVinci Resolve Studio.")
        return

    # Get list of projects in current folder
    projects = pm.GetProjectListInCurrentFolder()
    if not projects:
        show_error_dialog(
            ui,
            dispatcher,
            "No projects found in current folder.\n\nPlease ensure you have projects in the current database folder.",
        )
        return

    # Dialog 1: Select source project
    source_name = show_project_selection_dialog(ui, dispatcher, projects)
    if not source_name:
        return

    # Load source project
    source_project = pm.LoadProject(source_name)
    if not source_project:
        show_error_dialog(ui, dispatcher, f"Failed to load project:\n{source_name}")
        return

    # Get all settings from source project
    settings = source_project.GetSetting()

    # Check if settings were retrieved
    if not settings:
        show_error_dialog(
            ui,
            dispatcher,
            "No settings retrieved from project.\n\nThe project may not have any configurable settings.",
        )
        return

    if not isinstance(settings, dict):
        show_error_dialog(
            ui, dispatcher, f"Unexpected settings format.\n\nExpected dict, got {type(settings).__name__}"
        )
        return

    # Dialog 2: Enter new project name
    default_name = f"{source_name} Copy"
    new_name = show_name_input_dialog(ui, dispatcher, source_name, len(settings), default_name)
    if not new_name:
        return

    # Create new project
    new_project = pm.CreateProject(new_name)
    if not new_project:
        show_error_dialog(
            ui,
            dispatcher,
            f"Failed to create project:\n{new_name}\n\nThe project name may already exist in the current folder.",
        )
        return

    # Apply settings to new project
    success_count = 0
    failed_keys = []

    for key, value in settings.items():
        try:
            # Convert value to string as required by SetSetting API
            result = new_project.SetSetting(key, str(value))
            if result:
                success_count += 1
            else:
                failed_keys.append(key)
        except Exception:
            # Catch any exceptions during setting application
            failed_keys.append(key)

    # Dialog 3: Show results
    show_result_dialog(ui, dispatcher, new_name, success_count, len(settings), failed_keys)


if __name__ == "__main__":
    main()
