from cloud.kubios import kubios_analysis
from core.menu import get_menu_items, get_current_selection
from ui.layout_menu import show_menu


def handle_kubios():
    kubios_analysis()
    show_menu(get_menu_items(), get_current_selection())