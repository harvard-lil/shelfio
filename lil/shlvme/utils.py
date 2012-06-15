import datetime
import re


def get_current_year():
    now = datetime.datetime.now()
    return str(now.year)

def fill_with_get(form, get):
    for key in get:
        try:
            form.fields[key].initial = get[key]
        except KeyError:
            pass
        
def get_year_from_raw_date(raw_date):
    """We like displaying four digit years. Let's try to get those here"""
    
    #TODO flesh this out a bit. It now only works if we're passed something like 2003-02-08
    if len(raw_date) > 4:
        return raw_date[0:4]
    else:
        return raw_date
    
def get_numeric_page_count(page_count):
    """MARC tracks pagecounts, but they come in wild forms. Try to extract a number"""
    matches = re.search(r'([0-9]+)', page_count)
    
    if matches.group(1) and matches.group(1) > 0:
        return matches.group(1)

    return None
    