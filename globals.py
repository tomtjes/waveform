import configparser
from configparser import NoSectionError
import hashlib
from datetime import date, datetime
import re

class ConfigParser(configparser.ConfigParser):
    #Can get options() without defaults
    def options(self, section, no_defaults=False, **kwargs):
        if no_defaults:
            try:
                return list(self._sections[section].keys())
            except KeyError:
                raise NoSectionError(section)
        else:
            return super().options(section, **kwargs)

config = ConfigParser()

class Configuration:
    def __init__(self, name):
        self.name = name
        self.section = config[name]

CONFIG = Configuration("DEFAULT")
DATA = {'raw': '', 'reader': ''}
ERRORS = {}

class Transaction:
    def get_info(self, row, fields):
        if fields:
            fields = list(map(int, fields.split(',')))
            merged_text = ''
            for field in fields:
                merged_text += row[field].strip() + ' '
            return merged_text.strip()
        else:
            return('')

    def get_date(self, text, formats):
        for format in formats:
            try:
                return(datetime.strptime(text, format), format)
            except:
                pass
        ERRORS[len[ERRORS]] = { 'where': 'date', 'what': 'could not determine date' , 'who': [self.date, self.amount, self.description, self.notes]}
        return("ERROR: could not determine date", "")

    def get_amount(self,text):
        text = text.strip()
        # check if value negative
        if text[0] == '(' or text[0] == '-':
            neg = True
            text = text.strip('()- ')
        else:
            neg = False
        # remove separators from number
        separators = re.sub(r'\d', '', text, flags=re.U)
        for sep in separators[:-1]:
            text = text.replace(sep, '')
        if separators:
            try:
                # is the last separator a decimal separator (within last three characters of text)?
                text.index(separators[-1],-3)
                text = text.replace(separators[-1], '.')
            except:
                text = text.replace(separators[-1], '')
        # restore negative state
        if neg:
            text = '-' + text

        return(float(text))

    def get_id(self, row, idfield, idexclusions, method, transaction):
        id = ''
        if idfield and row[idfield]:
            return row[idfield].strip()
        elif not method:
            ERRORS[len[ERRORS]] = { 'where': 'id', 'what': 'unique ID expected, but not found' , 'who': [self.date, self.amount, self.description, self.notes]}
            return "ERROR: no unique ID found in data. Change your configuration to create ID when missing."
        elif method == "1":
            for t in transaction:
                if isinstance(t, datetime):
                    v = t.strftime('%Y-%m-%d')
                else:
                    v = t
                id = id + str(v)
        elif method == "2":
            if idexclusions: # False if "off"
                for ex in idexclusions:
                    row.pop(ex)
            id = ''.join(row)
        else:
            ERRORS[len[ERRORS]] = { 'where': 'id', 'what': 'unique ID could not be created' , 'who': [self.date, self.amount, self.description, self.notes]}
            return "ERROR: unique identifier not found. Adjust configuration."
        id = id.encode()
        return hashlib.md5(id).hexdigest()
    
    def searchreplace(self, fld, type, search, replace):
        if type == 'simple':
            setattr(self, fld, getattr(self, fld).replace(search,replace))
        elif type == 'regex':
            setattr(self, fld, re.sub(search,replace,getattr(self, fld)))
    
    def __init__(self, row={}, fields={}):
        if row and fields:
            self.date, _ = self.get_date(row[fields['date']],formats=fields['date format'])
            self.amount = self.get_amount(row[fields['amount']])
            self.description = self.get_info(row, fields['description'])
            self.notes = self.get_info(row, fields['notes'])
            self.id = self.get_id(row, fields['id'], fields['id exclusions'], fields['method'], [self.date, self.amount, self.description, self.notes])