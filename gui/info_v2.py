# from gui.color import coloredText
#
#
# print(coloredText('error', 'y'))


import sys
from consolemenu import *
from consolemenu.format import *
from consolemenu.items import *
from consolemenu.menu_component import Dimension
import webbrowser
from gui.color import coloredText


def main():

    header = ".              _      _____.__                 __      _____                                            . " \
             ".             (_)   _/ ____\__|______  _______/  |_  _/ ____\___________    _____   ____                . " \
             ".              _    \   __\|  \_  __ \/  ___/\   __\ \   __\ _  __ \__  \  /     \_/ __ \\               . " \
             ".             (_)    |  |  |  ||  | \/\___ \  |  |    |  |   |  | \// __ \|  Y Y  \  ___/               . " \
             ".                    |__|  |__||__|  /____  > |__|    |__|   |__|  (____  /__|_|  /\___  >              . " \
             ".                                         \/                            \/      \/     \/               . "

    menu_format = MenuFormatBuilder(max_dimension=Dimension(width=120))\
        .set_border_style_type(MenuBorderStyleType.HEAVY_BORDER) \
        .set_prompt(">>> ") \
        .set_title_align('center') \
        .set_subtitle_align('center') \
        .set_left_margin(4) \
        .set_right_margin(4) \
        .show_header_bottom_border(True)

    # Create the root menu
    menu = ConsoleMenu('BulkChanger', 'Version 0.3 by Florian Gemperle', prologue_text=header, formatter=menu_format)

    bulk = MenuItem('Start BulkChanger', menu)
    info = MenuItem('Start InfoCollector', menu)
    function_item = FunctionItem('Visit Homepage', webbrowser.open('https://www.firstframe.net'))


    # Create a menu item that calls a system command, based on OS type
    if sys.platform.startswith('win'):
        command_item = CommandItem("Command", 'cmd /c \"echo this is a shell. Press enter to continue." && set /p=\"')
    else:
        command_item = CommandItem("Command", 'sh -c \'echo "this is a shell. Press enter to continue."; read\'')

    # Create a submenu using a Selection Menu, which takes a list of strings to create the menu items.
    submenu = SelectionMenu(["item1", "item2", "item3"], title="Selection Menu",
                            subtitle="These menu items return to the previous menu")

    # Create the menu item that opens the Selection submenu
    submenu_item = SubmenuItem("Submenu item", submenu=submenu)
    submenu_item.set_menu(menu)

    # Create a second submenu, but this time use a standard ConsoleMenu instance
    submenu_2 = ConsoleMenu("Another Submenu Title", "Submenu subtitle.")
    function_item_2 = FunctionItem("Fun item", Screen().input, ["Enter an input: "])
    item2 = MenuItem("Another Item")
    submenu_2.append_item(function_item_2)
    submenu_2.append_item(item2)
    submenu_item_2 = SubmenuItem("Another submenu", submenu=submenu_2)
    submenu_item_2.set_menu(menu)

    # Add all the items to the root menu
    menu.append_item(bulk)
    menu.append_item(info)
    menu.append_item(function_item)

    # Show the menu
    menu.start()
    menu.join()


if __name__ == "__main__":
    main()