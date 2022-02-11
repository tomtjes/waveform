from waveform_helpers import *
from waveform_globals import CONFIG as c, DATA as d, Transaction
import waveform_setup as setup
import waveform_search as search
import waveform_wave as wave

def get_fields():
    fields = {}
    fields['date'] = c.section.getint('Date')
    fields['date format'] = [c.section.get('Date Format',raw=True).replace('%%','%')]
    fields['amount'] = c.section.getint('Amount')
    fields['description'] = c.section.get('Description')
    fields['notes'] = c.section.get('Notes', fallback='')
    fields['id'] = c.section.get('Unique Identifier', fallback='')
    if fields['id']:
        fields['id'] = int(fields['id'])
    fields['method'] = c.section.get('Unique Identifier Method',fallback='')
    id_exclusions = c.section.get('Unique Identifier Exclusions', fallback='')
    if id_exclusions:
        try:
            id_exclusions = list(map(int, id_exclusions.split(',')))
        except:
            id_exclusions = c.section.getboolean('Unique Identifier Exclusions')
    fields['id exclusions'] = id_exclusions
    return fields

def get_transactions(fields):
    d['raw'].seek(0)
    transactions = []
    for row in list(d['reader'])[1:]:
        t = Transaction(row,fields)
        transactions.append(t)
    return transactions

def main_csv_to_wave(config_name='', file=''):
    
    if not file:
        file = get_csv()
    
    read_csv(file)

    if not config_name:
        if not setup.select():
            return
    else:
        c.__init__(config_name)

    fields = get_fields()

    if any(field is None for field in (fields['date'], fields['date format'], fields['amount'], fields['description'])):
        print("ERROR in configuration: missing values. Edit your configuration. ")
        return

    transactions = get_transactions(fields)
    transactions = search.replace(transactions)
  
    print("\nFound the following transactions:\n")
    print('{:10} {:>10} {:25} {:25} {:25}'.format("DATE", "AMOUNT", "DESCRIPTION", "NOTES", "ID"))
    for t in transactions:
        print('{} {:>10.2f} {:25} {:25} {:25}'.format(t.date.strftime('%Y-%m-%d'), t.amount, (t.description[:22] + "...") if len(t.description)>25 else t.description, (t.notes[:22] + "...") if len(t.notes)>25 else t.notes, (t.id[:22] + "...") if len(t.id)>25 else t.id))

    if not yes_no("\nDo you want to post these to your Wave account now? "):
        print("\nABORTING\n")
        return

    for t in transactions:
        if t.amount < 0:
            dir = "WITHDRAWAL"
            inc_exp = c.section.get('Account Expense')
        else:
            dir = "DEPOSIT"
            inc_exp = c.section.get('Account Income')
        vars={
    "input": {
      "businessId": c.section.get('Business'),
      "externalId": t.id,
      "date": t.date.strftime("%Y-%m-%d"),
      "description": t.description,
      "notes": t.notes,
      "anchor": {
        # Eg. Business checking account
        "accountId": c.section.get('Account'),
        "amount": "{:.2f}".format(t.amount).replace('-',''),
        "direction": dir
      },
      "lineItems": [{
        # Eg. Sales Account
        "accountId": inc_exp,
        "amount": "{:.2f}".format(t.amount).replace('-',''),
        "balance": "INCREASE"
      }]
    }
  }
        resp = wave.mutate(vars)
        resp = resp['data']['moneyTransactionCreate']
        if resp['didSucceed']:
            print("\nSUCCESS: Transaction created.")
        else:
            print("\nERROR: " + resp['inputErrors'][0]['message'])
            print("Failed transaction: ")
            print('{} {:>10.2f} {:25} {:25} {:25}'.format(
                t.date.strftime('%Y-%m-%d'), 
                t.amount, 
                (t.description[:22] + "...") if len(t.description)>25 else t.description, 
                (t.notes[:22] + "...") if len(t.notes)>25 else t.notes, 
                (t.id[:22] + "...") if len(t.id)>25 else t.id))
    return