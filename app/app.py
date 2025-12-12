"""
Main application loop for the device UI.

This module wires together the rotary encoder input, the menu system, the
display, and several action handlers (heart rate measurement, HRV analysis,
Kubios export/processing, and viewing history). The goal of the run_app
function is to continuously poll the encoder for rotation and button presses,
update the currently visible menu accordingly, and dispatch to the correct
handler when the user selects a menu item and presses the encoder button.

Detailed behaviour documented inline below.
"""

from core.menu import (
    get_menu_items,
    get_current_selection,
    update_selection,
    get_current_item
)

# `Encoder` is a hardware abstraction for a rotary encoder device. It provides
# methods to read rotation turns and may be tied to specific GPIO pins.
# `is_encoder_pressed` is a helper that returns whether the encoder button
# (press action) is currently pressed. `encoder_button` is the raw pin object
# for the physical button so code can read its `value()` directly when needed.
from core.utils import Encoder, is_encoder_pressed, encoder_button

# `show_menu` renders the current menu items and highlights the current
# selection on the attached display. It expects a list of menu items and the
# index (or identifier) of the currently selected item.
from ui.display import show_menu

# Import handler functions for each top-level menu action. These are small
# modules that encapsulate the behaviour for each menu item. Some handlers
# (like `handle_measure_hr` and `handle_history`) accept the `encoder` object
# so they can interact with the same input device while the handler runs.
from app.handle_hr import handle_measure_hr 
from app.handle_hrv import handle_basic_hrv
from app.handle_kubios import handle_kubios
from app.handle_history import handle_history
from core.local_mqtt import connect_wifi, connect_mqtt, publish_json

import time


def run_app():
    """
    Start the main event loop that reads user input and updates the UI.

    Behaviour summary:
    - Initialize the encoder (hardware input) on two GPIO pins.
    - Draw the initial menu to the display.
    - Enter an infinite loop that:
      * Polls the encoder for rotation (left/right turns).
        - If rotation is detected, update menu selection and refresh the display.
      * Polls whether the encoder button is pressed.
        - If pressed, wait for a stable press, determine which menu item is
          selected, and call the handler for that item.
        - After the handler returns, wait for button release and a fresh
          press cycle before returning to the menu display (prevents accidental
          re-entry into a handler due to bouncing or lingering button state).

    Notes on debouncing and waiting:
    - The code uses short `time.sleep(0.05)` delays to yield CPU time and to
      provide a simple debounce mechanism for mechanical button presses.
    - There are two separate checks around button handling:
      1) `is_encoder_pressed()` is a higher-level helper to check if the
         button is pressed (used to detect the initial press event).
      2) `encoder_button.value()` reads the raw hardware pin value; it is
         checked directly to wait for the pin to go high/low as appropriate.
      This combination ensures the code waits for both press and release
      transitions reliably.
    """

    # Initialize encoder hardware abstraction using two GPIO pins (example
    # pin numbers 10 and 11). The exact pins and wiring depend on your
    # microcontroller board and `Encoder` implementation.
    encoder = Encoder(10, 11)

    # Draw the initial menu to the screen using the menu helpers from core.menu
    show_menu(get_menu_items(), get_current_selection())

    # Main polling loop: runs forever until the device is powered off or
    # the process is terminated. This loop is intentionally simple and
    # deterministic for embedded environments without a full event system.
    while True:
        # Check for rotary encoder rotation. `get_turn()` should return a
        # non-zero value when the encoder has been rotated since the last
        # check. The value often indicates direction (+1 / -1) or steps.
        turn = encoder.get_turn() 
        if turn:
            # Update the menu selection based on rotation direction and
            # then redraw the menu to reflect the new selection.
            update_selection(turn)
            show_menu(get_menu_items(), get_current_selection())

        # Check whether the encoder's push-button is pressed. `is_encoder_pressed`
        # is a helper that returns True if a press is detected; it abstracts
        # away any specific pin-level logic and may also include debouncing.
        if is_encoder_pressed():
            # Wait for the encoder button to be fully pressed (pin value 0).
            # This loop pauses until the raw button pin reads 0 indicating the
            # actual hardware has settled into the pressed state. A short sleep
            # prevents a tight busy loop and reduces CPU usage on microcontrollers.
            while encoder_button.value() == 0:
                time.sleep(0.05)

            # Determine which menu item is currently selected so we can call
            # the appropriate handler function below.
            selected = get_current_item()

            # Dispatch to the correct handler based on the selected item label.
            # These labels (e.g. "MEASURE HR") are provided by the menu system
            # and should match the strings used here. Handlers encapsulate the
            # behaviour for each feature and may block until the feature is
            # finished (for example a measurement sequence).
            if selected == "MEASURE HR":
                # Start a heart rate measurement flow. We pass the `encoder`
                # instance so the measurement UI can still receive rotation and
                # press events while the measurement UI is active.
                handle_measure_hr(encoder)
            elif selected == "HRV ANALYSIS":
                # Run a basic HRV analysis routine. This handler does not
                # require the encoder reference in this code, so it is called
                # without arguments.
                handle_basic_hrv()
            elif selected == "KUBIOS":
                # Trigger Kubios-related behaviour (exporting or processing
                # data compatible with Kubios). Exact behaviour depends on
                # `app.handle_kubios` implementation.
                handle_kubios()
            elif selected == "HISTORY":
                # Show or manage measurement history. The handler receives
                # the `encoder` object to allow the history UI to navigate
                # lists or pages using the same input device.
                handle_history(encoder)

            # After the handler returns, wait until the user releases the
            # press and then ensures the encoder button goes through a full
            # press-release cycle before returning to the menu. This prevents
            # immediate re-entry into handlers due to the same button state
            # lingering (mechanical bounce or user holding the button).
            while not is_encoder_pressed():
                time.sleep(0.05)
            while encoder_button.value() == 0:
                time.sleep(0.05)

            # Redisplay the menu once the handler has finished and the
            # physical button state is stable again.
            show_menu(get_menu_items(), get_current_selection())

        # Small sleep to limit loop frequency and reduce CPU usage. The
        # value 0.05 seconds gives 20Hz polling which is responsive enough
        # for human input while being gentle on microcontroller resources.
        time.sleep(0.05)
