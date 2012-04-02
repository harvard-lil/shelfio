import datetime


def get_current_year():
    now = datetime.datetime.now()
    return str(now.year)

def fill_with_get(form, get):
    for key in get:
        try:
            form.fields[key].initial = get[key]
        except KeyError:
            pass