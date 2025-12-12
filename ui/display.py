"""
UI display composition module for screen layout dispatching.

This module consolidates and re-exports all visual UI components used across
the application. It acts as a single entry-point for importing display logic,
enabling cleaner separation between logic and UI flow.

Includes:
- Menu UI (main navigation)
- HR/HRV measurement and results screens
- History views (list, details, back navigation)
- Countdown animations and ECG visualization
- Common display helpers (errors, placeholders, sending)
- OLED control object

This module does not define new functions but serves as a bridge for modular UI.
"""


from .layout_menu import show_menu
from .layout_hr import show_start_instruction, show_hr_screen
from .layout_hrv import show_hrv_screen, show_kubios_results
from .layout_history import show_history_list, show_measurement_detail, show_back_menu
from .layout_animations import show_countdown_animation, draw_ecg_frame
from .layout_common import show_placeholder, show_error_screen, show_sending_screen
from .oled import oled
