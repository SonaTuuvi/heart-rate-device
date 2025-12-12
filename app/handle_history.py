"""
History handler and UI navigation for previous measurements.

This module exposes `handle_history(encoder)` which is called from the main
menu when the user selects the "HISTORY" option. It loads saved measurement
records, filters and displays the most recent entries, and lets the user
navigate the list and view details for a selected measurement. Navigation
is performed using the same `encoder` object used elsewhere in the app.

Behaviour details and design notes are provided inline below.
"""

from ui.layout_history import show_history_list, show_measurement_detail, show_back_menu
from core.utils import is_encoder_pressed
from history.history_utils import load_history
import time

 
def handle_history(encoder):
    """
    Present recent measurement history and allow the user to inspect items.

    Args:
        encoder: The shared `Encoder` instance used for rotational input and
                 button presses. We use it to let the user move through the
                 list and to interact with detail views.

    High-level steps:
    1. Load all history entries from persistent storage via `load_history()`.
    2. Filter out invalid or empty measurements (for example entries with
       `mean_hr` <= 0) because these are not useful to display.
    3. Keep up to the last 5 valid entries (most recent) and show them.
    4. Allow the user to rotate the encoder to change the selection index.
    5. If the encoder button is pressed, show the detail view for the
       currently selected measurement and present a small back menu that
       lets the user return to the history list or go back to the main menu.

    Notes on UI behaviour:
    - `show_history_list(recent_history, index)` is responsible for rendering
      the list and visually highlighting the current `index`.
    - `show_measurement_detail(entry, encoder)` displays a single measurement
      in a detail view and may itself use the `encoder` for pagination or
      additional interactions while the detail view is active.
    - `show_back_menu(encoder)` returns a string choice made by the user
      in the small menu displayed after viewing details; the handler uses
      that value to decide whether to continue showing history or to return
      to the main application menu.
    - The function uses modular, small sleeps (`time.sleep(0.05)`) to reduce
      CPU usage and debounce mechanical input.
    """

    # Load stored history records. The format and structure of the returned
    # list are defined by `history.history_utils.load_history` (commonly a
    # list of dicts where each dict contains measurement metadata).
    history = load_history()
    
    # Filter out entries that are not real measurements. This example filters
    # using `mean_hr` (mean heart rate) which is expected to be > 0 for valid
    # records. The default value 0 is used when the key is missing.
    valid_history = [entry for entry in history if entry.get("mean_hr", 0) > 0]

    # Keep only the most recent five measurements so the UI is concise and
    # fits on small displays. Negative slicing gracefully handles shorter lists.
    recent_history = valid_history[-5:]

    # If no valid history exists, show an empty list placeholder and briefly
    # pause so the user can read the message, then return back to the caller
    # (which will typically redisplay the main menu).
    if not recent_history:
        show_history_list([], -1)
        time.sleep(2)
        return

    # Index of the currently selected item in the `recent_history` list.
    index = 0

    # Event loop for history navigation. This loop handles rotation-based
    # selection changes and button presses to enter the detail view. It
    # returns control to the caller only when the user chooses to go back to
    # the main menu.
    while True:
        # Render the list and highlight the current selection index.
        show_history_list(recent_history, index)

        # Read encoder rotation; `get_turn()` returns a delta (e.g. -1/1)
        # or 0 when there is no movement. We update the index and wrap using
        # modulo so the selection cycles through the list.
        turn = encoder.get_turn()
        if turn:
            index = (index + turn) % len(recent_history)

        # If the encoder button is pressed, enter the detailed view for the
        # currently selected measurement. The detail view may itself provide
        # further interactions and will return when finished.
        if is_encoder_pressed():
            show_measurement_detail(recent_history[index], encoder)

            # After viewing details, present a small back menu that asks the
            # user whether they want to return to the history list or go back
            # to the main application menu. The `show_back_menu` helper uses
            # the encoder for selection and returns a string representing
            # the user's choice.
            choice = show_back_menu(encoder)
            
            if choice == "BACK TO HISTORY":
                # User wants to continue browsing the history list; loop
                # continues and the list will be shown again.
                continue
            elif choice == "BACK TO MAIN":
                # User selected to return to the main menu; exit this handler
                # so the calling code can redraw the main menu.
                return

        # Delay a short time to avoid busy-waiting. This value controls the
        # responsiveness vs CPU usage trade-off for input polling.
        time.sleep(0.05)
