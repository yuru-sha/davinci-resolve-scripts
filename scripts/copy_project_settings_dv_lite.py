#!/usr/bin/env python3
"""
Copy Project Settings (Free Version)

This script copies all settings from an existing project to a new project in DaVinci Resolve.
Free version uses console-based interactive prompts.

Usage:
    Run this script from DaVinci Resolve: Workspace > Scripts > Utility > Copy Project Settings (Lite)
"""

import sys


def main():
    """Main function for copying project settings."""
    # Check if running inside DaVinci Resolve
    try:
        resolve_obj = resolve  # noqa: F821
    except NameError:
        print("ERROR: This script must be run within DaVinci Resolve.")
        sys.exit(1)

    # Get ProjectManager
    pm = resolve_obj.GetProjectManager()
    if not pm:
        print("ERROR: Failed to get ProjectManager.")
        return

    # Get list of projects in current folder
    projects = pm.GetProjectListInCurrentFolder()
    if not projects:
        print("ERROR: No projects found in current folder.")
        print("Please ensure you have projects in the current database folder.")
        return

    print("\n" + "=" * 50)
    print("Copy Project Settings (Free Version)")
    print("=" * 50)

    # Display available projects
    print("\nAvailable projects in current folder:")
    for i, name in enumerate(projects, 1):
        print(f"  {i}. {name}")

    # Get user selection
    choice = input(f"\nSelect source project (1-{len(projects)}): ").strip()
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(projects):
            raise ValueError
        source_name = projects[idx]
    except (ValueError, IndexError):
        print("ERROR: Invalid selection.")
        return

    # Load source project
    print(f"\nLoading '{source_name}'...")
    source_project = pm.LoadProject(source_name)
    if not source_project:
        print(f"ERROR: Failed to load project '{source_name}'.")
        return

    # Get all settings from source project
    print("Retrieving project settings...")
    settings = source_project.GetSetting()

    # Check if settings were retrieved
    if not settings:
        print("ERROR: No settings retrieved from project.")
        print("The project may not have any configurable settings.")
        return

    if not isinstance(settings, dict):
        print(f"ERROR: Unexpected settings format (type: {type(settings)}).")
        return

    print(f"Settings loaded: {len(settings)} items")

    # Get new project name with default
    default_name = f"{source_name} Copy"
    new_name = input(f"\nEnter new project name [{default_name}]: ").strip()
    if not new_name:
        new_name = default_name

    # Create new project
    print(f"\nCreating new project '{new_name}'...")
    new_project = pm.CreateProject(new_name)
    if not new_project:
        print(f"ERROR: Failed to create project '{new_name}'.")
        print("The project name may already exist in the current folder.")
        return

    # Apply settings to new project
    print("Applying settings to new project...")
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
        except Exception as e:
            # Catch any exceptions during setting application
            failed_keys.append(key)
            print(f"  Warning: Failed to apply '{key}': {e}")

    # Display results
    print("\n" + "=" * 50)
    print("Results")
    print("=" * 50)
    print(f"Project created: {new_name}")
    print(f"Settings applied: {success_count}/{len(settings)}")

    if failed_keys:
        print(f"\nFailed to apply {len(failed_keys)} setting(s):")
        for key in failed_keys[:10]:  # Show first 10 failed keys
            print(f"  - {key}")
        if len(failed_keys) > 10:
            print(f"  ... and {len(failed_keys) - 10} more")
        print("\nNote: Some settings may be read-only or version-specific.")
    else:
        print("\nAll settings applied successfully!")

    print("\nDone. New project has been created and loaded.")
    print("=" * 50)


if __name__ == "__main__":
    main()
