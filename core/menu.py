"""
Simple in-memory menu state helpers.

This module stores a small list of top-level menu item labels and exposes
helper functions used by the UI code to read the items, query the current
selection index, update the selection based on encoder rotation, and get
the currently selected label.

The helpers are intentionally minimal and operate on module-level state
which is sufficient for a single-screen embedded device. If you later need
multiple independent menus or re-entrant behaviour, consider encapsulating
menu state in a class.
"""

# Top-level menu labels shown in the main menu. Update this list to change
# what options appear in the device's main menu.
menu_items = [
    "MEASURE HR",
    "HRV ANALYSIS",
    "KUBIOS",
    "HISTORY"
]

# Index of the currently highlighted/selected menu item. The UI rendering
# code uses this index to highlight the current choice. Starts at 0 (first
# item) by default.
current_selection = 0


def get_menu_items():
    """Return the list of menu item labels.

    The UI display function calls this to obtain the items to render. The
    list itself is returned directly (not a copy) for simplicity; avoid
    mutating it in callers unless you intentionally want to modify the
    app menu.
    """

    return menu_items


def get_current_selection():
    """Return the integer index of the currently selected menu item."""

    return current_selection


def update_selection(direction):
    """
    Update the current selection index using `direction` and wrap around.

    Args:
        direction (int): Typically +1 or -1 indicating the encoder rotation
                         direction. The function updates the module-level
                         `current_selection` and wraps using modulo so the
                         selection cycles through the available items.
    """

    global current_selection
    current_selection = (current_selection + direction) % len(menu_items)


def get_current_item():
    """Return the label (string) of the currently selected menu item."""

    return menu_items[current_selection]
