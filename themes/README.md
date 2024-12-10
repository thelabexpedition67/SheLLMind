# **SheLLMind Themes Guide**

## **Introduction**
SheLLMind supports customizable themes to personalize the look and feel of your application. Themes are defined in **JSON files** and allow you to specify the color scheme for various components of the interface.

## **Theme File Structure**
Each theme is a JSON file that contains:
1. **name**: The name of the theme.
2. **description**: A short description of the theme.
3. **author**: The name of the creator.
4. **palette**: A list of style definitions for different interface components.

---

## **Example Theme JSON**
Here is an example of a valid theme file:

```json
{
  "name": "Sunset Horizon",
  "description": "A warm theme with glowing orange and red hues, inspired by a serene sunset.",
  "author": "ThemeForge",
  "palette": [
    {
      "name": "normal_linebox_border",
      "foreground": "brown",
      "background": null,
      "attributes": null,
      "description": "Line border of unfocused widget"
    },
    {
      "name": "focus_linebox_border",
      "foreground": "yellow",
      "background": null,
      "attributes": "bold",
      "description": "Line border of focused widget"
    },
    {
      "name": "menu_voice",
      "foreground": "light red",
      "background": null,
      "attributes": "bold",
      "description": "Highlighted menu voice divider"
    }
  ]
}
```

---

## **Explanation of Fields**

Each entry in the `palette` array defines one style for a specific part of the interface. Here's what each field means:

| Field        | Required | Description                                                                 |
|--------------|----------|-----------------------------------------------------------------------------|
| `name`       | **Yes**  | A unique identifier for the style (e.g., `normal_content`, `menu_voice`).   |
| `foreground` | **Yes**  | Text color. Set to any valid color (see list below) or `null` for default.  |
| `background` | **No**   | Background color. Set to any valid color or `null` for transparent/default. |
| `attributes` | **No**   | Text style attributes (e.g., `bold`, `underline`). See valid attributes below. |
| `description`| **No**   | A short description of what this style is for.                             |

---

## **Available Colors**
Below is the list of colors supported by **Urwid**. You can use these for both `foreground` and `background` fields:

### **Basic Colors**
- `black`
- `dark red`
- `dark green`
- `brown`
- `dark blue`
- `dark magenta`
- `dark cyan`
- `light gray`

### **Bright Colors**
- `dark gray`
- `light red`
- `light green`
- `yellow`
- `light blue`
- `light magenta`
- `light cyan`
- `white`

---

## **Attributes**
The `attributes` field allows you to add text styles. You can combine multiple attributes by separating them with a space.

| Attribute      | Description                                      |
|----------------|--------------------------------------------------|
| `bold`         | Makes the text bold.                            |
| `underline`    | Underlines the text.                            |
| `standout`     | Highlights the text (reverse video).            |
| `blink`        | Makes the text blink (may not work in all terminals). |
| `italics`      | Makes the text italicized (if supported).       |

**Example**:
```json
{
  "name": "menu_voice",
  "foreground": "light red",
  "background": null,
  "attributes": "bold underline",
  "description": "Highlighted menu voice with bold and underline"
}
```

---

## **Theme File Naming Convention**
- Theme files must be stored in the `themes` directory.
- The filename should end with `.json`. Example: `my_theme.json`
- The **name of the file** (without the `.json` extension) is used as the theme identifier in the application.

---

## **How to Create a Theme**
1. Create a new JSON file in the `themes` directory.
2. Use the structure outlined above to define the theme.
3. Save the file with a unique name, e.g., `forest_glow.json`.
4. Start SheLLMind and select your theme from the **Configuration Menu**.

---

## **Default Style Names**
Here are the default style names that you can customize in your theme:

| Style Name             | Description                                      |
|------------------------|--------------------------------------------------|
| `normal_linebox_border`| Border color for unfocused widgets.              |
| `focus_linebox_border` | Border color for focused widgets.                |
| `menu_voice`           | Style for menu items and dividers.               |
| `normal_content`       | Style for normal text.                           |
| `who`                  | Style for "You" and "AIm" prefixes in chat.      |
| `ai_message`           | Style for messages written by the AI.            |
| `user_message`         | Style for messages written by the user.          |
| `divider`              | Style for the divider line between messages.     |

---

## **Testing Your Theme**
1. Save your theme file in the `themes` directory.
2. Launch SheLLMind and go to the **Configuration Menu**.
3. Select **Theme Selection** to choose your new theme.
4. If there are any errors, they will be logged, and the default theme will be applied.

---

## **Troubleshooting**
- **Theme not appearing?**  
  Ensure your file is saved in the `themes` directory and has a `.json` extension.

- **Invalid colors?**  
  Double-check the colors used against the **Available Colors** list above.

- **Application crashes?**  
  Verify the JSON syntax using an online JSON validator.

---

## **Contributing Themes**
If you create a theme that you would like to share:
1. Test it thoroughly in SheLLMind.
2. Ensure the theme file includes your name and description.
3. Share your theme on the project's repository or via email.

---

## **Conclusion**
By creating and applying themes, you can customize SheLLMind to your preference. Whether you prefer vibrant, calming, or retro aesthetics, the flexibility of the theme system allows for limitless creativity.