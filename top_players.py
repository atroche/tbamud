#!/usr/bin/env python3
"""
Top Players Script for tbaMUD
Shows the top 10 players by XP and Gold with their classes.
"""

from dataclasses import dataclass
from pathlib import Path

# Class mappings from tbaMUD source (src/structs.h)
CLASS_NAMES = {
    0: "Magic User",
    1: "Cleric",
    2: "Thief",
    3: "Warrior",
}

CLASS_ICONS = {
    0: "🔮",
    1: "✝️",
    2: "🗡️",
    3: "⚔️",
}


@dataclass
class Player:
    name: str
    class_id: int
    level: int
    xp: int
    gold: int

    @property
    def class_name(self) -> str:
        return CLASS_NAMES.get(self.class_id, "Unknown")

    @property
    def class_icon(self) -> str:
        return CLASS_ICONS.get(self.class_id, "❓")


def parse_player_file(filepath: Path) -> Player | None:
    """Parse a .plr file and return a Player object."""
    try:
        content = filepath.read_text()
    except Exception:
        return None

    data = {
        "name": "",
        "class_id": 0,  # Default to Magic User if not specified
        "level": 0,
        "xp": 0,
        "gold": 0,
    }

    for line in content.splitlines():
        line = line.strip()
        if line.startswith("Name:"):
            data["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("Clas:"):
            try:
                data["class_id"] = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("Levl:"):
            try:
                data["level"] = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("Exp "):
            # Format is "Exp : 1234"
            try:
                data["xp"] = int(line.split(":", 1)[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.startswith("Gold:"):
            try:
                data["gold"] = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass

    if not data["name"]:
        return None

    return Player(**data)


def find_all_players(plrfiles_dir: Path) -> list[Player]:
    """Find and parse all player files."""
    players = []

    for subdir in plrfiles_dir.iterdir():
        if not subdir.is_dir():
            continue
        for plr_file in subdir.glob("*.plr"):
            player = parse_player_file(plr_file)
            if player:
                players.append(player)

    return players


def print_table(title: str, players: list[Player], sort_key: str, limit: int = 100):
    """Print a formatted table of players."""
    sorted_players = sorted(players, key=lambda p: getattr(p, sort_key), reverse=True)[:limit]

    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")
    print(f"{'Rank':<6} {'Player':<15} {sort_key.upper():<12} {'Class':<18} {'Level':<6}")
    print(f"{'-' * 60}")

    for i, player in enumerate(sorted_players, 1):
        value = getattr(player, sort_key)
        class_display = f"{player.class_icon} {player.class_name}"
        print(f"{i:<6} {player.name:<15} {value:<12,} {class_display:<18} {player.level:<6}")

    print()


def print_class_summary(players: list[Player], sort_key: str, limit: int = 10):
    """Print a summary of classes in the top players."""
    sorted_players = sorted(players, key=lambda p: getattr(p, sort_key), reverse=True)[:limit]

    class_counts: dict[int, int] = {}
    for player in sorted_players:
        class_counts[player.class_id] = class_counts.get(player.class_id, 0) + 1

    print("Class Distribution:")
    for class_id, count in sorted(class_counts.items(), key=lambda x: -x[1]):
        icon = CLASS_ICONS.get(class_id, "❓")
        name = CLASS_NAMES.get(class_id, "Unknown")
        print(f"  {icon} {name}: {count} player(s)")


def main():
    # Find the plrfiles directory relative to this script
    script_dir = Path(__file__).parent
    plrfiles_dir = script_dir / "lib" / "plrfiles"

    if not plrfiles_dir.exists():
        # Try current directory
        plrfiles_dir = Path("lib/plrfiles")

    if not plrfiles_dir.exists():
        print("Error: Could not find plrfiles directory")
        print(f"Looked in: {plrfiles_dir.absolute()}")
        return 1

    print(f"Reading player files from: {plrfiles_dir.absolute()}")

    players = find_all_players(plrfiles_dir)
    print(f"Found {len(players)} players")

    # Top 10 by XP
    print_table("🏆 TOP 10 PLAYERS BY XP", players, "xp")
    print_class_summary(players, "xp")

    # Top 10 by Gold
    print_table("💰 TOP 10 PLAYERS BY GOLD", players, "gold")
    print_class_summary(players, "gold")

    return 0


if __name__ == "__main__":
    exit(main())
