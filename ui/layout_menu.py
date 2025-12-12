"""
UI layout for main menu rendering.

This module provides a simple vertical list menu with a highlighted selection
indicator. It is designed for use with rotary encoder navigation where only
one item is active at a time.

Displayed format:
- Selected item is prefixed with "> "
- Others are prefixed with two spaces
- Supports up to 6 visible menu items (1 per 10 pixels vertically)
"""


from .oled import oled

def show_menu(items, selected_index):
    """
    Render a vertical menu with highlight on the selected item.

    Behaviour:
    - Clears the OLED screen.
    - Displays each item in order.
    - Adds "> " prefix to selected item, space prefix to others.

    Args:
        items (list[str]): List of menu item strings to display.
        selected_index (int): Index of the currently selected item.
    """
    
    oled.fill(0)
    for i, item in enumerate(items):
        prefix = "> " if i == selected_index else "  "
        oled.text(prefix + item, 0, i * 10)
    oled.show()
