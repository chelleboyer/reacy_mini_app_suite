# TTKBootstrap Themes in Reachy Remix

Reachy Remix now includes beautiful theme support inspired by [ttkbootstrap](https://ttkbootstrap.readthedocs.io/), giving you 9 gorgeous themes to choose from!

## Available Themes

### Light Themes ☀️

#### Cosmo
- **Primary**: Blue (#2780E3)
- **Accent**: Purple (#9954BB)
- Clean, modern Bootstrap-inspired design

#### Flatly
- **Primary**: Dark Blue-Gray (#2C3E50)
- **Accent**: Turquoise (#18BC9C)
- Flat design with contemporary colors

#### Minty (Default)
- **Primary**: Mint Green (#78C2AD)
- **Accent**: Pink (#F3969A)
- Fresh, playful, kid-friendly aesthetic

#### Pulse
- **Primary**: Purple (#593196)
- **Accent**: Light Purple (#A991D4)
- Bold and energetic color scheme

### Dark Themes 🌙

#### Solar
- **Primary**: Gold (#B58900)
- **Accent**: Teal (#2AA198)
- Inspired by the Solarized Dark theme

#### Darkly
- **Primary**: Navy (#375A7F)
- **Accent**: Turquoise (#00BC8C)
- Classic dark theme with Bootstrap styling

#### Cyborg
- **Primary**: Cyan (#2A9FD6)
- **Accent**: Gray (#555555)
- High-tech, futuristic aesthetic

#### Superhero
- **Primary**: Orange (#DF691A)
- **Accent**: Light Blue (#5BC0DE)
- Bold, comic book-inspired colors

#### Vapor
- **Primary**: Hot Pink (#EA00D9)
- **Accent**: Cyan (#0ABDC6)
- Vaporwave/synthwave aesthetic

## How to Use

### In the UI
1. Look for the **Theme** dropdown in the top-right corner
2. Select any theme from the dropdown
3. The app will display a confirmation message
4. Refresh the page to see the new theme applied

### Programmatically
```python
from reachy_remix import create_theme, get_custom_css

# Create a theme
theme = create_theme("cyborg")

# Get custom CSS for a theme
css = get_custom_css("vapor")
```

## Theme Features

Each theme includes:
- **Color-coordinated UI**: All buttons, backgrounds, and text adapt to the theme
- **Gradient effects**: Move buttons use smooth gradients
- **Consistent styling**: Border colors, shadows, and accents match the theme
- **Accessibility**: Proper contrast ratios for readability
- **Dark mode support**: Dark themes adjust text and background colors

## Customization

The theme system is extensible. To add a new theme:

```python
TTKBOOTSTRAP_THEMES["mytheme"] = {
    "name": "My Theme",
    "type": "light",  # or "dark"
    "primary": "#HEX_COLOR",
    "secondary": "#HEX_COLOR",
    "success": "#HEX_COLOR",
    "info": "#HEX_COLOR",
    "warning": "#HEX_COLOR",
    "danger": "#HEX_COLOR",
    "bg": "#HEX_COLOR",
    "fg": "#HEX_COLOR",
}
```

## Implementation Details

The theme system:
1. **Gradio Theme**: Uses `gr.themes.Soft()` as base with custom colors
2. **Custom CSS**: Dynamic CSS generation based on theme colors
3. **Global State**: Theme persists via global variables
4. **Hot Reload**: Theme changes require page refresh (Gradio limitation)

## Credits

Themes inspired by:
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) by Israel Dryer
- [Bootswatch](https://bootswatch.com/) Bootstrap themes
- Bootstrap framework color system
