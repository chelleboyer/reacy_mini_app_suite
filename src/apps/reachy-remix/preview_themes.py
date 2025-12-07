#!/usr/bin/env python3
"""
Theme Preview - View all TTKBootstrap-inspired themes
Generates a visual preview of all available themes
"""

# TTKBootstrap-inspired theme definitions (standalone copy)
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
        "bg": "#FFFFFF",
        "fg": "#373A3C",
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
        "bg": "#FFFFFF",
        "fg": "#2C3E50",
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
        "bg": "#FFFFFF",
        "fg": "#5A5A5A",
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
        "bg": "#FFFFFF",
        "fg": "#444444",
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
        "bg": "#002B36",
        "fg": "#839496",
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
        "bg": "#222222",
        "fg": "#AAAAAA",
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
        "bg": "#060606",
        "fg": "#ADAFAE",
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
        "bg": "#2B3E50",
        "fg": "#EBEBEB",
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
        "bg": "#1A1A2E",
        "fg": "#E5E5E5",
    }
}

def print_theme_preview():
    """Print a text-based preview of all themes."""
    
    print("=" * 70)
    print("🎨 REACHY REMIX - TTKBOOTSTRAP THEMES PREVIEW")
    print("=" * 70)
    print()
    
    # Group by type
    light_themes = {k: v for k, v in TTKBOOTSTRAP_THEMES.items() if v["type"] == "light"}
    dark_themes = {k: v for k, v in TTKBOOTSTRAP_THEMES.items() if v["type"] == "dark"}
    
    print("☀️  LIGHT THEMES")
    print("-" * 70)
    for key, theme in light_themes.items():
        print(f"\n  {theme['name'].upper()} ({key})")
        print(f"    Primary:   {theme['primary']}")
        print(f"    Secondary: {theme['secondary']}")
        print(f"    Success:   {theme['success']}")
        print(f"    Info:      {theme['info']}")
        print(f"    Warning:   {theme['warning']}")
        print(f"    Danger:    {theme['danger']}")
    
    print("\n" + "=" * 70)
    print("🌙 DARK THEMES")
    print("-" * 70)
    for key, theme in dark_themes.items():
        print(f"\n  {theme['name'].upper()} ({key})")
        print(f"    Primary:   {theme['primary']}")
        print(f"    Secondary: {theme['secondary']}")
        print(f"    Success:   {theme['success']}")
        print(f"    Info:      {theme['info']}")
        print(f"    Warning:   {theme['warning']}")
        print(f"    Danger:    {theme['danger']}")
        print(f"    BG:        {theme['bg']}")
        print(f"    FG:        {theme['fg']}")
    
    print("\n" + "=" * 70)
    print(f"\nTotal themes available: {len(TTKBOOTSTRAP_THEMES)}")
    print("  Light themes:", len(light_themes))
    print("  Dark themes:", len(dark_themes))
    print()
    print("To use a theme, select it from the dropdown in the Reachy Remix UI")
    print("or run: python reachy_remix.py")
    print("=" * 70)


def generate_html_preview():
    """Generate an HTML file showing all theme colors."""
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Reachy Remix Theme Preview</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { text-align: center; color: #333; }
        .theme-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .theme-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .theme-header {
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 5px;
            color: white;
        }
        .color-swatch {
            display: flex;
            align-items: center;
            margin: 8px 0;
            font-size: 0.9em;
        }
        .color-box {
            width: 40px;
            height: 40px;
            border-radius: 5px;
            margin-right: 10px;
            border: 2px solid #ddd;
        }
        .section-title {
            font-size: 2em;
            margin: 30px 0 15px 0;
            padding: 10px;
            border-left: 5px solid #007bff;
        }
    </style>
</head>
<body>
    <h1>🎨 Reachy Remix Theme Preview</h1>
    <p style="text-align: center;">TTKBootstrap-inspired themes for your robot dance builder</p>
"""
    
    # Group themes
    light_themes = {k: v for k, v in TTKBOOTSTRAP_THEMES.items() if v["type"] == "light"}
    dark_themes = {k: v for k, v in TTKBOOTSTRAP_THEMES.items() if v["type"] == "dark"}
    
    def render_theme_section(themes, title, icon):
        section = f'<div class="section-title">{icon} {title}</div><div class="theme-grid">\n'
        for key, theme in themes.items():
            section += f'''
    <div class="theme-card">
        <div class="theme-header" style="background: {theme['primary']};">
            {theme['name']}
        </div>
        <div class="color-swatch">
            <div class="color-box" style="background: {theme['primary']};"></div>
            <span><strong>Primary:</strong> {theme['primary']}</span>
        </div>
        <div class="color-swatch">
            <div class="color-box" style="background: {theme['secondary']};"></div>
            <span><strong>Secondary:</strong> {theme['secondary']}</span>
        </div>
        <div class="color-swatch">
            <div class="color-box" style="background: {theme['success']};"></div>
            <span><strong>Success:</strong> {theme['success']}</span>
        </div>
        <div class="color-swatch">
            <div class="color-box" style="background: {theme['info']};"></div>
            <span><strong>Info:</strong> {theme['info']}</span>
        </div>
        <div class="color-swatch">
            <div class="color-box" style="background: {theme['warning']};"></div>
            <span><strong>Warning:</strong> {theme['warning']}</span>
        </div>
        <div class="color-swatch">
            <div class="color-box" style="background: {theme['danger']};"></div>
            <span><strong>Danger:</strong> {theme['danger']}</span>
        </div>
    </div>
'''
        section += '</div>\n'
        return section
    
    html += render_theme_section(light_themes, "Light Themes", "☀️")
    html += render_theme_section(dark_themes, "Dark Themes", "🌙")
    
    html += """
    <footer style="text-align: center; margin-top: 40px; color: #666;">
        <p>Inspired by <a href="https://ttkbootstrap.readthedocs.io/">ttkbootstrap</a> 
        and <a href="https://bootswatch.com/">Bootswatch</a></p>
    </footer>
</body>
</html>
"""
    
    return html


if __name__ == "__main__":
    import sys
    
    # Print text preview
    print_theme_preview()
    
    # Generate HTML if requested
    if "--html" in sys.argv:
        html = generate_html_preview()
        output_file = "theme_preview.html"
        with open(output_file, "w") as f:
            f.write(html)
        print(f"\n✅ HTML preview generated: {output_file}")
        print(f"   Open it in a browser to see all themes!")
