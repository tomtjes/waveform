import copy
from waveform_globals import config
from waveform_helpers import *
import waveform_post as post

def replace(transactions, searches={}):
    if not searches:
        searches = read()
    for s in sorted(searches):
        for t in transactions:
            t.searchreplace(searches[s]['field'],searches[s]['type'],searches[s]['search'][1:-1],searches[s]['replace'][1:-1])
    return transactions

def read():
    searches = {}
    for o in (opt for opt in config.options(c.name,no_defaults=True) if "search" in opt):
        #option format is e.g. "notes simple search 1" or "description regex search 2"
        searches[int(o.split()[3])] = {'search': c.section.get(o), 'type' : o.split()[1], 'field' : o.split()[0]}

    for o in (opt for opt in config.options(c.name,no_defaults=True) if "replace" in opt):
        searches[int(o.split()[3])]['replace'] = c.section.get(o)
    return searches

def update():
    print('\nThe search/replace patterns you will enter need to be validated.')
    csv_file = get_csv()
    read_csv(csv_file)

    searches = read()
    if searches:
        menu_options = {}
        for s in sorted(searches):
            menu_options[s-1] = '{:12}  {:6}  {:35}  {:20}'.format(searches[s]['field'],searches[s]['type'],searches[s]['search'],searches[s]['replace'])
        print("\nYou have the following searches configured, which are executed in this order. Which one do you want to edit?\n")
        print('     {:12}  {:6}  {:35}  {:20}'.format("FIELD","TYPE","SEARCH","REPLACE"))
        print("-"*80, end = '')
        menu_options[len(menu_options)] = "ADD NEW SEARCH/REPLACE PATTERN"
        options = print_menu(menu_options)
        opt = menu_select(options)
        if opt == -1:
            print("\nNo option selected.")
            return
        
        if opt == len(menu_options)-1:
            config_menu()
        else:
            edit(searches[opt+1]['type'], searches[opt+1]['field'], update = opt+1)
    else:
        # no searches configured yet
        config_menu()
    return

def edit(type, field, update=''):
    edit = False

    while True:
        searches = read()

        if update:
            edit = True
            srch = searches[update]['search']
            repl = searches[update]['replace']

        if edit:
            print('\nTo delete a search leave the search field empty.')
            print("\nYou previously entered:")
            print("Search:  " + srch)
            print("Replace: " + repl + "\n")

        srch = str(input('\nEnter new ' + type + ' search phrase for ' + field + ': '))
        srch = '"' + srch + '"' # add quotes to string to preserve leading and trailing white space in config
        repl = str(input('\nEnter replacement: '))
        repl = '"' + repl + '"'

        if update:
            searches[update] = {'search': srch, 'type' : type, 'field' : field, 'replace' : repl}
        else:
            searches[len(searches)+1] = {'search': srch, 'type' : type, 'field' : field, 'replace' : repl}

        print('\nYou have defined the following search-and-replace patterns for "' + c.name + '":\n')
        print('{:12}  {:6}  {:35}  {:20}'.format("FIELD","TYPE","SEARCH","REPLACE"))
        print("-"*80)
        for s in sorted(searches):
            if update and update == s:
                print("\n|||||||||||| CURRENT EDIT BELOW ||||||||||||||||||||||||||||||||||||")
            print('{:12}  {:6}  {:35}  {:20}'.format(searches[s]['field'],searches[s]['type'],searches[s]['search'],searches[s]['replace']))
            if update and update == s:
                print("|||||||||||| CURRENT EDIT ABOVE ||||||||||||||||||||||||||||||||||||\n")
        print("\nYour search/replace patterns affect your transactions in the following ways:")
        
        fields = post.get_fields()
        transactions = post.get_transactions(fields)
        transactions_old = copy.deepcopy(transactions)
        transactions_new = replace(transactions, searches)

        for i, (o, n) in enumerate(zip(transactions_old,transactions_new)):
            print("\n------  TRANSACTION " + str(i+1) + "  ------")
            print("Description before: " + o.description)
            print("Description after:  " + n.description)
            print("")
            print("Notes before:       " + o.notes)
            print("Notes after:        " + n.notes)

        if yes_no("\nDoes this look as intended?"):
            
            nothingtodo = False

            # no search pattern given?
            if not srch.strip('"'):
                if update:
                    # delete all existing search patterns (recreate below)
                    for opt in config.options(c.name):
                        if 'search' in opt:
                            config.remove_option(c.name,opt)
                            config.remove_option(c.name,opt.replace('search','replace'))
                    searches.pop(update)
                    print("\nSearch/replace pattern removed.")
                else:
                    nothingtodo = True
            
            if nothingtodo:
                print("Search pattern empty. Nothing to save.")
            else:
            # renumber search options
                for i, s in enumerate(sorted(searches)):      
                    c.section[searches[s]['field'] + " " + searches[s]['type'] + " search " + str(i+1)] = searches[s]['search']
                    c.section[searches[s]['field'] + " " + searches[s]['type'] + " replace " + str(i+1)] = searches[s]['replace']
            
                print("\nSearch/replace patterns saved.")
        
                config_write()  

            if yes_no("\nDo you want to add another search pattern?"):
                return config_menu()
            else:
                return
        else:
            menu_options = { 0: "Edit my search pattern", 1: "Cancel"}
            options = print_menu(menu_options)
            opt = menu_select(options,False)
            if opt == 0:
                edit = True
            else:
                return

def config_menu():
    print("\nYou can modify your data with search and replace, if you want to change recurring patterns in your transactions.")
    menu_options = { 
        0: "Create simple search-and-replace rule for DESCRIPTIONS",
        1: "Create simple search-and-replace rule for NOTES",
        2: "Create regex search-and-replace rule for DESCRIPTIONS",
        3: "Create regex search-and-replace rule for NOTES"}
    options = print_menu(menu_options)
    opt = menu_select(options)
    if opt == -1:
        print("\nNo search/replace configured.")
        return
    elif opt == 0:
        edit("simple","description")
    elif opt == 1:
        edit("simple","notes")
    elif opt == 2:
        edit("regex","description")
    elif opt == 3:
        edit("regex","notes")
    return