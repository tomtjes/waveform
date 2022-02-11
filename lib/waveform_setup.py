from waveform_globals import config, Transaction, CONFIG as c
from waveform_helpers import *
import waveform_wave as wave
import waveform_search as search

def set_name(update=False):
    while True:
        new_name = input("\nPlease provide a name for this configuration: ")
        if config.has_section(new_name) and new_name != c.name:
            print("Configuration " + new_name + " already exists. Try again.")
        elif new_name != c.name:
            config.add_section(new_name)
            print("\nConfiguration created.")
            if update:
                for opt, val in config.items(c.name, raw=True):
                    config[new_name][opt] = val
                config.remove_section(c.name)
            c.__init__(new_name)
            break
        elif new_name == c.name:
            print("\nNew name is identical to old name. Nothing to do here.")
            break
    return

def get_formatting (update = False):
    csv_file = get_csv()
    read_csv(csv_file)
    
    col_names = []
    for row_num, row in enumerate(list(d['reader'])[0:6]):
        if row_num > 0:
            print("\n------------------------ TRANSACTION " + str(row_num) + " ------------------------\n")
            print('{:>5}  {:25}  {}'.format("", "NAME", "CONTENT"))
        for col_num, field in enumerate(row):
            if field.strip() == "":
                continue
            if row_num == 0:
                col_names.append(field)
            else:
                print('{:>2} {:2}  {:25}  {}'.format(col_num, "--", col_names[col_num], field))
    
    print("\nAbove, you find up to 5 transactions from the provided file. Please check them while creating your configuration. Enter the respective NUMBER that you find at the beginning of the line.")
    
    print("\nWhich row shows the transaction AMOUNT?")
    if update: print ("(Press ENTER to keep [" + c.section.get('Amount') + "]) ")
    get_config_input('Amount', True)

    print("\nWhat do you want to use as the transaction DESCRIPTION (appears in the transaction list in Wave)?\nYou can enter multiple, comma-separated numbers.")
    if update: print ("(Press ENTER to keep [" + c.section.get('Description') + "]) ")
    get_config_input('Description', True)

    print("\nWhat do you want to use as the transaction NOTES (appears in transaction details in Wave?)?\nYou can enter multiple, comma-separated numbers. This is optional and can be left empty.")
    if update: print ("(Press ENTER to keep [" + c.section.get('Notes') + "]) ")
    get_config_input('Notes')
    
    # unique identifier
    print("\nEach transaction needs a unique ID. Transactions with a previously used ID will not be posted to Wave.")
    menu_options = { 0: "My data contains a unique ID for each transaction",
    1: "My data contains a unique ID for some transactions",
    2: "My data does not contain unique IDs" }
    r = print_menu(menu_options)
    r = menu_select(r)

    if r == 0 or r == 1:
        print("\nWhich row contains the unique IDs?")
        if update and c.section.get('Unique Identifier'):
            print("(Press ENTER to keep [" + c.section.get('Unique Identifier') + "]. Use SPACE to delete the value and use automatically generated identifiers.) ")
        c.section['Unique Identifier'] = str(input() or c.section.get('Unique Identifier',fallback=''))
    
    if r==1 or r == 2:
        print("\nWhen the data doesn't contain a unique ID, it needs to be created. There are two possible methods for that, which each have their advantages and disadvantages.")
        menu_options = { 0: "METHOD 1: The ID is based on the transaction date, amount, description and notes. This method will fail only when all of these parameters are identical for two transactions. This method will still work, if the format of your CSV data changes.",
    1: "METHOD 2: The ID is based on extended transaction data (if data contains more than date, amount, description and notes, that additional data will be considered). That makes it more unlikely that two IDs will turn out to be identical. This method will fail to recognize that a transaction has been posted to Wave before, when the format of your data changes, which can lead to duplicate entries in Wave."}
        m = print_menu(menu_options)
        if update and c.section.get('Unique Identifier Method', fallback=''): 
            print ("(Currently configured: " + c.section.get('Unique Identifier Method') + ")")
        m = menu_select(m)
        c.section['Unique Identifier Method'] = str(m+1)
        if m == 1:
            print("\nAs explained above, this method relies on constant data. Please go back and look at the transactions above and check, if there are any rows that are not constant, i.e. that could be different when you export some of the transactions again. For instance, some banks and banking apps number the transactions in a CSV file. This number is not constant across multiple data exports and must therefore be excluded from generating a unique transaction ID.")
            print("Anything that might not be constant should be added here, comma-separated. ")
            if 'unique identifier exclusions' in config.options(c.name, no_defaults=True):
                print("(Press ENTER to keep [" + c.section.get('Unique Identifier Exclusions') + "]. Enter SPACE to revert to default of " + config.get('DEFAULT','Unique Identifier Exclusions') + "].) ")
            elif update:
                print("Press ENTER to keep the default value [" + config.get('DEFAULT','Unique Identifier Exclusions') + "].")
            else:
                print("Press ENTER to use the default value [" + config.get('DEFAULT','Unique Identifier Exclusions') + "].")
            
            if 'unique identifier exclusions' in config.options(c.name,no_defaults=True):
                c.section['Unique Identifier Exclusions'] = str(input('Enter OFF to not exclude anything from ID generation.\n') or c.section.get('Unique Identifier Exclusions',fallback=''))
            else:
                c.section['Unique Identifier Exclusions'] = str(input('Enter OFF to not exclude anything from ID generation.\n'))
    
    # date + validation
    print("\nOkay, that was complicated, but necessary. Here's an easy one:")
    print("Which row shows the transaction DATE?")
    if update: print ("(Press ENTER to keep [" + c.section.get('Date') + "]) ")
    get_config_input('Date', True)
    
    print("\nAwesome. Let's check if the dates can be read. Here are the transaction dates from your file and how they're interpreted:\n")
    date_field = c.section.getint('Date')
    formats = ('%m/%d/%Y', '%m/%d/%y', '%Y/%m/%d', '%b%d/%Y', '%d.%m.%Y', '%d.%m.%y', '%d-%m-%Y', '%Y-%m-%d')
    while True:
        print('YOUR CSV  -> -> YYYY-MM-DD')
        print('--------------------------')
        d['raw'].seek(0)
        for row in list(d['reader'])[1:6]:
            t = Transaction()
            test_date, format = t.get_date(row[date_field], formats)
            print('{:14}  {}'.format(row[date_field], test_date.strftime('%Y-%m-%d')))
        if yes_no("\nDoes this look correct? "):
            c.section['Date Format'] = format.replace('%','%%')
            return
        else:
            formats = [input("Date format detection failed. Please enter date format manually. Use directives from https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes, e.g. %m/%d/%y ")]

def main_create():
    if not config.get('DEFAULT','Token', fallback=''):
        print("\nERROR: You don't have access to Wave configured. Please do that first.\n")
        return
    
    c.__init__('DEFAULT')
    set_name()

    if not wave.get_business():
        return

    if not wave.get_account():
        return

    print('\nNext, we need to configure INCOME and EXPENSE accounts for your transactions. Select "Uncategorized Income" or "Uncategorized Expense" if you\'re not sure.')
    if not wave.get_inc_exp_account('INCOME'):
        return
    if not wave.get_inc_exp_account('EXPENSE'):
        return

    get_formatting()

    if yes_no("\nEnter advanced config (search and replace)?"):
        search.config_menu()

    config_write()

    return

def select():
    sections = config.sections()
    if len(sections) > 1:
        print("\nAvailable import configurations:")
        r = print_menu(dict(enumerate(sections)))
        r = menu_select(r,False)
    elif len(sections) < 1:
        print("\nERROR: No configurations found. Please create one first.")
        return False
    else:
        r = 0
        print('\nOnly one configuration found. Continuing with "' + sections[r] + '".')
    c.__init__(sections[r])
    return True

def main_update():
    if select():
        menu_options = { 
        0: "Change name of configuration",
        1: "Change Wave business or accounts",
        2: "Change how the CSV files are interpreted",
        3: "Change search-and-replace patterns",
        4: "Delete configuration"}
        r = print_menu(menu_options)
        r = menu_select(r)
        if r == -1:
            print("\nCancel.")
            return
        elif r == 0:
            set_name(True)
        elif r == 1:
            wave.update_wave()
        elif r == 2:
            get_formatting(True)
        elif r == 3:
            search.update()
        elif r == 4:
            config.remove_section(c.name)
            print("\nConfiguration " + c.name + " deleted")
            c.__init__('DEFAULT')
        config_write()
    return