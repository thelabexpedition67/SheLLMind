import json
import os
from debug import debug

class Themes:
    THEMES_DIRECTORY = "themes"

    def __init__(self, default_palette):
        """
        Initialize Themes with a default palette.
        """
        self.default_palette = default_palette
        self.current_theme = {}

    def validate_theme_json(self, theme_data):
        """
        Validate theme JSON to ensure required keys are present.
        """
        for entry in theme_data.get("palette", []):
            if not entry.get("name"):
                raise ValueError("Palette entry missing 'name' key.")
            if entry.get("foreground") is None:
                entry["foreground"] = ""
            if entry.get("background") is None:
                entry["background"] = ""

    def load_theme(self, theme_name):
        """
        Load a theme JSON file and update the palette.
        :param theme_name: The theme file name without extension (e.g., '0' for 0.json).
        """
        if theme_name=="default":
            return self.default_palette

        theme_file = os.path.join(self.THEMES_DIRECTORY, f"{theme_name}.json")

        if not os.path.exists(theme_file):
            debug(f"Theme file '{theme_file}' not found. Using default theme.")
            return self.default_palette

        try:
            with open(theme_file, "r") as file:
                theme_data = json.load(file)
                self.validate_theme_json(theme_data)
                self.current_theme = theme_data.get("palette", [])
        except (json.JSONDecodeError, KeyError, Exception) as e:
            debug(f"Failed to load theme '{theme_name}': {e}. Using default theme.")
            return self.default_palette

    def _merge_palette(self):
        """
        Merge loaded theme palette with the default palette.
        """
        # Convert default palette into a dictionary for easier updates
        palette_dict = {entry[0]: entry for entry in self.default_palette}

        # Update palette with current theme values
        for theme_entry in self.current_theme:
            name = theme_entry.get("name")
            fg = theme_entry.get("foreground") or "default"  # Replace None or "" with "default"
            bg = theme_entry.get("background") or "default"
            attr = theme_entry.get("attributes", "")

            # Update the palette entry
            if name in palette_dict:
                debug(f"Overwriting '{name}': {fg}, {bg}, {attr}")  # Debug log
                palette_dict[name] = (name, fg, bg, attr)
            else:
                debug(f"Adding new palette entry: '{name}': {fg}, {bg}, {attr}")  # Debug log
                palette_dict[name] = (name, fg, bg, attr)

        # Final merged palette
        merged_palette = list(palette_dict.values())
        debug(f"Final palette: {merged_palette}")  # Debug log
        return merged_palette