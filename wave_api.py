import requests
import webbrowser
from globals import config
from helpers import *

wave_endpoint = "https://gql.waveapps.com/graphql/public"

def get_headers():
  token = config.get('DEFAULT','Token',fallback='')
  headers = {"Authorization": "Bearer " + token}
  return headers

def query(q, vars='{}'):
  h = get_headers()
  return requests.post(wave_endpoint, json={'query': q, 'variables': vars}, headers=h).json()

def mutate(vars):
  h = get_headers()
  mutation="""mutation ($input:MoneyTransactionCreateInput!){
  moneyTransactionCreate(input:$input){
    didSucceed
    inputErrors{
      path
      message
      code
    }
    transaction{
      id
    }
  }
}"""
  return requests.post(wave_endpoint, json={'query': mutation, 'variables': vars}, headers=h).json()

# configure Wave access
def main_get_token():
    if config.get('DEFAULT','Token', fallback='') and not yes_no("You already have an access token configured. Do you want to replace it?"):
        print("Back to main menu.\n")
        return

    print("""
    To give this script access to Wave, you need to register it with Wave.
    If you continue, Wave will open in your browser. 
    Login to your account and create an application. Name it 'waveform' and save.
    Open the application and create a Full Access Token. 

    W A R N I N G
    THIS TOKEN IS A KEY TO YOUR WAVE ACCOUNT.
    WAVEFORM STORES IT UNENCRYPTED IN A TEXT FILE ON YOUR COMPUTER.
    PROCEED WITH CAUTION.
    """)
    if not yes_no("Do you want to continue? "):
        print("\nCanceling.")
        return

    print('\nOpening Wave in your browser. Please follow the steps described above.')
    webbrowser.open('https://developer-apps.waveapps.com/apps/')

    config['DEFAULT']['Token'] = str(input("\nEnter your token: ")).strip()
    print('\nTrying to access Wave...\n')

    q = """query {
  user {
    firstName
    lastName
    defaultEmail
  }  
}"""
    r = query(q)
    resp = r['data']['user']
    usr = resp['firstName'] + " " + resp['lastName'] + ", " + resp['defaultEmail']
    print("Is this the account you want to connect?")
    if yes_no(usr):
        config_write()
        print('Access to Wave successfully configured.')
    else:
        config['DEFAULT']['Token'] = ''
        print('Access to Wave configuration ABORTED.\n')   
    return

def query_business():
    q = """query {
  businesses {
    edges {
      node {
        id
        name
        isPersonal
      }
    }
  }
}"""
    resp = query(q)
    resp = resp['data']['businesses']['edges']
    businesses = {}
    for num, biz in enumerate(resp): 
        if biz['node']['isPersonal']:
            biz['node']['name'] = biz['node']['name'] + " (personal)"
        del biz['node']['isPersonal']
        businesses[num] = biz['node']
    return businesses

def get_business():
    if not config.get('DEFAULT','Business',fallback='') or not yes_no("\nYou have a default business configured. Do you want to use it for this bank account?"):
        businesses = query_business()

        retval = print_menu(businesses,'name')
        print('Which business do you want to use? ')
        retval = menu_select(retval)
        if retval == -1:
            print("\nNo business configured.")
            return False

        biz = businesses[retval]['id']

        if yes_no("Do you want to save this business as default (will affect all configurations that use the default business)?"):
            config['DEFAULT']['Business'] = biz
        else:
            c.section['Business'] = biz
        print('Business successfully configured.')
    return True

def eval_account(resp):
    resp = resp['data']['business']['accounts']['edges']
    print("\nFound the following accounts:")
    accounts = {}
    for i, acc in enumerate(resp):
      #  if acc['node']['notes']:
      #      acc['node']['name'] = acc['node']['name'] + " (" + acc['node']['notes'] + ")"
      #  del acc['node']['description']
        accounts[i] = acc['node']
    return accounts

def get_account():
    q = """query ($businessId: ID!) {
  business(id: $businessId) {
    id
    accounts(subtypes: [CASH_AND_BANK, CREDIT_CARD, LOANS], isArchived: false) {
      edges {
        node {
          id
          name
          description
          normalBalanceType
        }
      }
    }
  }
}"""
    operation_vars = { "businessId": c.section.get('Business') }
    resp = query(q, operation_vars)
    accounts = eval_account(resp)

    retval = print_menu(accounts,'name')
    print('Which account do you want to use? ')
    retval = menu_select(retval)
    if retval == -1:
        print("\nNo account configured.")
        return False

    c.section['Account'] = accounts[retval]['id']
    print('\nAccount successfully configured.')
    return True

def get_inc_exp_account(type, update=False):
    q = """query ($businessId: ID!, $type: [AccountTypeValue!]) {
  business(id: $businessId) {
    id
    accounts(types: $type, isArchived: false) {
      edges {
        node {
          id
          name
          description
          normalBalanceType
        }
      }
    }
  }
}"""
    operation_vars = { "businessId": c.section.get('Business'), "type" : type }
    resp = query(q, operation_vars)
    accounts = eval_account(resp)

    if update:
        accounts[len(accounts)] = ({"name" : "CANCEL and keep currently configured account", "id" : c.section['Account ' + type]})

    retval = print_menu(accounts,'name')
    print('Which ' + type + ' account do you want to use?')
    retval = menu_select(retval)
    if retval == -1:
        print("\nNo account configured.")
        return False

    c.section['Account ' + type] = accounts[retval]['id']
    print('\n' + type + ' account successfully configured.')
    return True

def update_wave():
    menu_options = { 
    0: "Update selected Wave business",
    1: "Update Income Account",
    2: "Update Expense Account"}
    r = print_menu(menu_options)
    r = menu_select(r)
    if r == -1:
        print("\nCancel.")
        return
    elif r == 0:
        get_business()
    elif r == 1:
        get_inc_exp_account('INCOME', True)
    elif r == 2:
        get_inc_exp_account('EXPENSE', True)
    return