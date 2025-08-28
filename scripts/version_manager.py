#!/usr/bin/env python3
"""
Script to help manage versions and releases for geosquare-grid.

This script uses setuptools_scm to automatically determine the version
from Git tags and provides utilities for creating releases.
"""

import subprocess
import sys
import argparse
from typing import Optional


def run_command(cmd: str) -> str:
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(
            cmd.split(), capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{cmd}': {e}")
        sys.exit(1)


def get_current_version() -> str:
    """Get the current version using setuptools_scm."""
    try:
        import setuptools_scm
        return setuptools_scm.get_version()
    except ImportError:
        print("setuptools_scm not installed. Installing...")
        run_command("pip install setuptools_scm")
        import setuptools_scm
        return setuptools_scm.get_version()


def get_latest_tag() -> Optional[str]:
    """Get the latest Git tag."""
    try:
        return run_command("git describe --tags --abbrev=0")
    except:
        return None


def create_tag(version: str, message: Optional[str] = None) -> None:
    """Create a Git tag for the given version."""
    if message is None:
        message = f"Release version {version}"
    
    print(f"Creating tag {version} with message: {message}")
    run_command(f"git tag -a {version} -m '{message}'")
    print(f"Tag {version} created successfully!")
    print("Don't forget to push the tag: git push origin --tags")


def main():
    parser = argparse.ArgumentParser(description="Manage versions and releases")
    parser.add_argument("--current", action="store_true", 
                       help="Show current version")
    parser.add_argument("--latest-tag", action="store_true",
                       help="Show latest Git tag")
    parser.add_argument("--create-tag", type=str, metavar="VERSION",
                       help="Create a new Git tag with the specified version")
    parser.add_argument("--message", type=str, metavar="MESSAGE",
                       help="Tag message (used with --create-tag)")
    
    args = parser.parse_args()
    
    if args.current:
        print(f"Current version: {get_current_version()}")
    
    if args.latest_tag:
        latest = get_latest_tag()
        if latest:
            print(f"Latest tag: {latest}")
        else:
            print("No tags found")
    
    if args.create_tag:
        create_tag(args.create_tag, args.message)
    
    if not any([args.current, args.latest_tag, args.create_tag]):
        print(f"Current version: {get_current_version()}")
        latest = get_latest_tag()
        if latest:
            print(f"Latest tag: {latest}")
        else:
            print("No tags found")


if __name__ == "__main__":
    main()
