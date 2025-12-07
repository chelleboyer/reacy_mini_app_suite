# Reachy Remix - Theme Update

## 🎨 NEW: TTKBootstrap Theme Support!

Reachy Remix now includes **9 beautiful themes** inspired by the popular [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) library!

### Quick Start

1. **Launch Reachy Remix:**
   ```bash
   python src/apps/reachy-remix/reachy_remix.py
   ```

2. **Change Theme:**
   - Look for the "Theme" dropdown in the top-right corner
   - Select any of the 9 available themes
   - Refresh your browser to apply the new theme

3. **Preview All Themes:**
   ```bash
   # Text preview in terminal
   python src/apps/reachy-remix/preview_themes.py
   
   # Generate HTML gallery
   python src/apps/reachy-remix/preview_themes.py --html
   open src/apps/reachy-remix/theme_preview.html
   ```

### Available Themes

**Light Themes (4):**
- 🌊 **Cosmo** - Blue and purple, modern Bootstrap
- 🏢 **Flatly** - Dark blue-gray, contemporary
- 🌿 **Minty** (Default) - Fresh mint green, kid-friendly
- 💜 **Pulse** - Bold purple, energetic

**Dark Themes (5):**
- ☀️ **Solar** - Solarized Dark (gold/teal)
- 🌑 **Darkly** - Classic dark Bootstrap
- 🤖 **Cyborg** - High-tech cyan
- 🦸 **Superhero** - Comic book orange/blue
- 🌌 **Vapor** - Vaporwave aesthetic (hot pink/cyan)

### Features

✅ Dynamic color schemes for all UI elements  
✅ Proper contrast for light and dark themes  
✅ Smooth gradient effects on buttons  
✅ Theme-aware borders and shadows  
✅ Easy theme switching via dropdown  
✅ Professional, kid-friendly aesthetics  

### Documentation

- **Full Theme Guide:** [docs/THEMES.md](../docs/THEMES.md)
- **Implementation Details:** [docs/other-apps/THEME_IMPLEMENTATION.md](../docs/other-apps/THEME_IMPLEMENTATION.md)
- **Visual Preview:** `src/apps/reachy-remix/theme_preview.html`

### Example: Switching to Vapor Theme

```python
# The theme system automatically handles everything!
# Just select "vapor" from the dropdown and refresh
```

### Credits

Themes inspired by:
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) by Israel Dryer
- [Bootswatch](https://bootswatch.com/) Bootstrap themes
- Modern web design best practices

---

**Enjoy the beautiful new themes!** 🎉 Perfect for kids, demos, and showcasing Reachy's personality!
