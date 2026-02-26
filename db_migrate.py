#!/usr/bin/env python
"""
Helper script untuk database migrations

Usage:
    python db_migrate.py upgrade      # Jalankan semua pending migrations
    python db_migrate.py downgrade    # Undo last migration
    python db_migrate.py current      # Lihat current revision
    python db_migrate.py history      # Lihat migration history
"""

import sys
import os
from alembic.config import Config
from alembic import command


def get_alembic_config():
    """Get Alembic config"""
    config = Config("alembic.ini")
    
    # Load settings from .env
    from config import settings
    config.set_main_option("sqlalchemy.url", settings.database_url)
    
    return config


def upgrade(revision="head"):
    """Upgrade database ke revision tertentu (default: latest)"""
    config = get_alembic_config()
    print(f"📦 Upgrading database to {revision}...")
    try:
        command.upgrade(config, revision)
        print("✓ Database upgraded successfully")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def downgrade(revision="-1"):
    """Downgrade database"""
    config = get_alembic_config()
    print(f"↩️  Downgrading database ({revision})...")
    try:
        command.downgrade(config, revision)
        print("✓ Database downgraded successfully")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def current():
    """Lihat current revision"""
    config = get_alembic_config()
    print("📍 Current database revision:")
    try:
        command.current(config)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def history():
    """Lihat migration history"""
    config = get_alembic_config()
    print("📋 Migration history:")
    try:
        command.history(config)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def create_migration(message=""):
    """Buat migration baru"""
    config = get_alembic_config()
    if not message:
        message = input("Enter migration description: ")
    
    print(f"✏️  Creating migration: {message}")
    try:
        command.revision(config, message=message, autogenerate=True)
        print("✓ Migration created successfully")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    if command == "upgrade":
        revision = args[0] if args else "head"
        upgrade(revision)
    elif command == "downgrade":
        revision = args[0] if args else "-1"
        downgrade(revision)
    elif command == "current":
        current()
    elif command == "history":
        history()
    elif command == "create":
        message = args[0] if args else ""
        create_migration(message)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
