#!/usr/bin/env python3
"""
Quick Theme Test - Preview theme colors in terminal with color codes
Requires a terminal that supports ANSI color codes
"""

TTKBOOTSTRAP_THEMES = {
    "cosmo": {
        "name": "Cosmo",
        "type": "light",
        "primary": "#2780E3",
        "secondary": "#373A3C",
        "success": "#3FB618",
        "info": "#9954BB",
        "warning": "#FF7518",
        "danger": "#FF0039",
    },
    "flatly": {
        "name": "Flatly",
        "type": "light",
        "primary": "#2C3E50",
        "secondary": "#95A5A6",
        "success": "#18BC9C",
        "info": "#3498DB",
        "warning": "#F39C12",
        "danger": "#E74C3C",
    },
    "minty": {
        "name": "Minty",
        "type": "light",
        "primary": "#78C2AD",
        "secondary": "#F3969A",
        "success": "#56CC9D",
        "info": "#6CC3D5",
        "warning": "#FFCE67",
        "danger": "#FF7851",
    },
    "pulse": {
        "name": "Pulse",
        "type": "light",
        "primary": "#593196",
        "secondary": "#A991D4",
        "success": "#13B955",
        "info": "#009CDC",
        "warning": "#EBA31D",
        "danger": "#FC3939",
    },
    "solar": {
        "name": "Solar",
        "type": "dark",
        "primary": "#B58900",
        "secondary": "#2AA198",
        "success": "#859900",
        "info": "#268BD2",
        "warning": "#CB4B16",
        "danger": "#DC322F",
    },
    "darkly": {
        "name": "Darkly",
        "type": "dark",
        "primary": "#375A7F",
        "secondary": "#444444",
        "success": "#00BC8C",
        "info": "#3498DB",
        "warning": "#F39C12",
        "danger": "#E74C3C",
    },
    "cyborg": {
        "name": "Cyborg",
        "type": "dark",
        "primary": "#2A9FD6",
        "secondary": "#555555",
        "success": "#77B300",
        "info": "#9933CC",
        "warning": "#FF8800",
        "danger": "#CC0000",
    },
    "superhero": {
        "name": "Superhero",
        "type": "dark",
        "primary": "#DF691A",
        "secondary": "#5BC0DE",
        "success": "#5CB85C",
        "info": "#5BC0DE",
        "warning": "#F0AD4E",
        "danger": "#D9534F",
    },
    "vapor": {
        "name": "Vapor",
        "type": "dark",
        "primary": "#EA00D9",
        "secondary": "#0ABDC6",
        "success": "#711C91",
        "info": "#0ABDC6",
        "warning": "#EA00D9",
        "danger": "#F50057",
    }
}


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def print_color_block(color_hex, label):
    """Print a colored block using ANSI escape codes."""
    r, g, b = hex_to_rgb(color_hex)
    # ANSI escape code for RGB background color
    print(f"  \033[48;2;{r};{g};{b}m    \033[0m {label:12} {color_hex}")


def preview_themes():
    """Display all themes with colored blocks."""
    print("\n" + "=" * 70)
    print("🎨 REACHY REMIX THEMES - COLOR PREVIEW")
    print("=" * 70 + "\n")
    
    # Group by type
    light_themes = {k: v for k, v in TTKBOOTSTRAP_THEMES.items() if v["type"] == "light"}
    dark_themes = {k: v for k, v in TTKBOOTSTRAP_THEMES.items() if v["type"] == "dark"}
    
    print("☀️  LIGHT THEMES")
    print("-" * 70)
    for key, theme in light_themes.items():
        print(f"\n  {theme['name'].upper()} ({key})")
        print_color_block(theme['primary'], "Primary")
        print_color_block(theme['secondary'], "Secondary")
        print_color_block(theme['success'], "Success")
        print_color_block(theme['info'], "Info")
        print_color_block(theme['warning'], "Warning")
        print_color_block(theme['danger'], "Danger")
    
    print("\n" + "=" * 70)
    print("🌙 DARK THEMES")
    print("-" * 70)
    for key, theme in dark_themes.items():
        print(f"\n  {theme['name'].upper()} ({key})")
        print_color_block(theme['primary'], "Primary")
        print_color_block(theme['secondary'], "Secondary")
        print_color_block(theme['success'], "Success")
        print_color_block(theme['info'], "Info")
        print_color_block(theme['warning'], "Warning")
        print_color_block(theme['danger'], "Danger")
    
    print("\n" + "=" * 70)
    print(f"Total themes: {len(TTKBOOTSTRAP_THEMES)} ({len(light_themes)} light, {len(dark_themes)} dark)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        preview_themes()
    except Exception as e:
        print(f"Error: {e}")
        print("Your terminal may not support ANSI color codes.")
        print("Try running: python preview_themes.py --html")
