from colorama import Fore, Style, init
init(autoreset=True)

BANNER = f"""
{Fore.RED}
    ____   _____ __   __ _   _ _______ 
   / __ \ / ____|\ \ / /| \ | |__   __|
  | |  | | (___   \ V / |  \| |  | |   
  | |  | |\___ \   > <  | . ` |  | |   
  | |__| |____) | / . \ | |\  |  | |   
   \____/|_____/ /_/ \_\|_| \_|  |_|   
{Fore.CYAN}         developed by : alzzdevmaret
{Style.RESET_ALL}
"""

def show_banner():
    print(BANNER)
