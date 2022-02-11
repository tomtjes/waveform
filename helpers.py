import os
import csv
from globals import CONFIG as c, DATA as d, config

def yes_no(text):
    while True:
        yn = input(text + " [y/n] ")
        if yn.lower() not in ('y', 'n'):
            print("Not an appropriate choice.\n")
        else:
            if yn.lower() == 'n':
                return False
            else:
                return True

def print_menu(optdict,key1=''):
    print('')
    if key1:
        for key in optdict.keys():
            print (key+1, '--', optdict[key][key1] )
    else:
        for key in optdict.keys():
            print (key+1, '--', optdict[key] )
    print('')
    return(len(optdict))

def menu_select(count,cancel_opt=True):
    while True:
        option = ''
        if cancel_opt:
            try:
                option = int(input('Enter the number of your choice (0 to cancel): '))
                if option <= count and option >= 0:
                    return option-1
                else:
                    print('Invalid option. Please enter a number between 1 and ', count, '.')
            except:
                print('Wrong input. Please enter a number.\n')
        else:
            try:
                option = int(input('Enter the number of your choice: '))
                if option <= count and option > 0:
                    return option-1
                else:
                    print('Invalid option. Please enter a number between 1 and ', count, '.')
            except:
                print('Wrong input. Please enter a number.\n')

def read_csv(file):
    d['raw'] = open(file,'r')
    dialect = csv.Sniffer().sniff(d['raw'].read(1024))
    d['raw'].seek(0)
    d['reader'] = csv.reader(d['raw'], dialect)
    return

def get_csv():
    print("\nPlease provide the path of a CSV file containing transactions.\nYou can drag and drop the file here (enter QUIT to quit): ")
    csv_file = input()
    while csv_file.lower() != 'quit':
        if not os.path.isfile(csv_file):
            print("Could not find file. Try again.")
            csv_file = input()
        else: 
            return csv_file
    exit()

def get_path():
    configpath = os.path.join(
    os.environ.get('APPDATA') or
    os.environ.get('XDG_CONFIG_HOME') or
    os.path.join(os.environ['HOME'], '.config'),
    "waveform")
    os.makedirs(configpath, exist_ok=True)
    return configpath

def config_read():
    configpath = get_path()
    if not os.path.isfile(configpath + '/waveform.conf'):
        # as a default exclude the first column from hashing, because it's likely an enumeration of rows.
        config['DEFAULT']['Unique Identifier Exclusions'] = '0'
    else:
        config.read(configpath + '/waveform.conf')
    return

def config_write():
    configpath = get_path()
    # delete empty options
    if c.name != 'DEFAULT':
        for opt in config.options(c.name,no_defaults=True):
            if not c.section.get(opt):
                config.remove_option(c.name,opt)

    # write file
    with open(configpath + '/waveform.conf', 'w') as configfile:
        config.write(configfile)
    print("\nConfiguration saved.")
    return

def get_config_input(field, mandatory=False):
    c.section[field] = str(input() or c.section.get(field, fallback=''))
    if mandatory:
        while not c.section.get(field).strip():
            print("Value for " + field.upper() + " can't be empty.")
            c.section[field] = str(input() or c.section.get(field ,fallback=''))