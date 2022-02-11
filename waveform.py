import argparse
import pathlib
from helpers import *
from globals import ERRORS as e, config as c
import wave_api as wave
import setup as setup
import post as post

def main_menu():
    while True:
        e.clear()
        print("\nMAIN MENU")
        menu_options = {
        0: 'Configure access to your Wave account',
        1: 'Create import configuration for a bank account',
        2: 'Edit an import configuration',
        3: 'Import a CSV file to Wave',
        4: 'Help',
        5: 'Exit'}
        r = print_menu(menu_options)
        r = menu_select(r,False)
        print("\n" + menu_options[r].upper() )    
        if r == 0:
            wave.main_get_token()
        elif r == 1:
            setup.main_create()
        elif r == 2:
            setup.main_update()
        elif r == 3:
            post.main_csv_to_wave()
        elif r == 4:
            parser = create_parser()
            parser.print_help()
        elif r == 5:
            exit()

def create_parser():
    parser = argparse.ArgumentParser(description='Waveform posts transactions from a csv file to waveapps.com.',
                    epilog="""You can start Waveform without any arguments to launch an interactive menu.
                    This should especially be used on first run in order to configure it.
                    Once configured, you can skip the menu and directly post a csv file to wave as described above under 'usage'.""")
    parser.add_argument('config', nargs='?', choices = c.sections(),
                        help='Name of a previously created import configuration for a specific csv format and Wave account. If this is empty, create configuration by running Waveform without arguments.')
    parser.add_argument('file', metavar='path/to/file.csv', type=pathlib.Path, nargs='?', 
                    help='CSV file to be imported to Wave.')
    return parser

## execute
e.clear()
config_read()

parser = create_parser()
args = parser.parse_args()

if args.config and args.file:
    post.main_csv_to_wave(args.config, args.file)
else:
    main_menu()