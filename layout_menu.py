from ui.oled import oled
import framebuf
import time
from menu_icons import menu_icons, ICON_WIDTH, ICON_HEIGHT

def welcome_screen():
    """
    Display the welcome screen with animated text.
    After animation, proceed to the main menu.
    """
    welcome_text = "SaaRi HR Monitor"
    
    oled.fill(0)
    for i in range(1, len(welcome_text)+1):
        oled.fill(0)
        partial = welcome_text[:i]
        oled.text(partial, (oled.width - len(partial) * 8) // 2, oled.height // 2)
        oled.show()
        time.sleep(0.1)  # animation speed (delay between letters)

    time.sleep(1.5)  # short pause before showing the menu

    # Go to the main menu (select first item)
    items = list(menu_icons.keys())
    show_menu(items, 0)






def show_menu(items, selected_index):
    """
    Render a screen with only the selected menu item and its icon.
    """
    oled.fill(0)

    # Get the selected label and its corresponding icon data
    selected_label = items[selected_index]
    icon_data = menu_icons.get(selected_label)

    # Draw the icon centered on the screen
    if icon_data:
        fb = framebuf.FrameBuffer(icon_data, ICON_WIDTH, ICON_HEIGHT, framebuf.MONO_HLSB)
        x = (oled.width - ICON_WIDTH) // 2
        y = 5  # slight vertical offset from top
        oled.blit(fb, x, y)

    # Draw the label text below the icon
    text_y = ICON_HEIGHT + 10
    oled.text(selected_label, (oled.width - len(selected_label) * 8) // 2, text_y)

    oled.show()
