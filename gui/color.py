from colorama import Fore, Back, Style

# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
# Style: DIM, NORMAL, BRIGHT, RESET_ALL

def coloredText(text, fore, back=None):
    # r, g, y, m, c, w
    output = Style.BRIGHT

    if fore.upper() == 'R':
        output = output + Fore.RED
    elif fore.upper() == 'G':
        output = output + Fore.GREEN
    elif fore.upper() == 'Y':
        output = output + Fore.YELLOW
    elif fore.upper() == 'M':
        output = output + Fore.MAGENTA
    elif fore.upper() == 'C':
        output = output + Fore.CYAN
    else:
        output = output + Fore.WHITE

    output = output + text + Style.RESET_ALL
    return output