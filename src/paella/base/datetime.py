from mx import DateTime


a_day = DateTime.oneDay
a_week = DateTime.oneWeek
example_format = '%m/%d/%Y %H:%M:%S'


def str2dt(datetime_string):
    return DateTime.DateFrom(datetime_string)

def date(datetime_string):
    return str2dt(datetime_string).date

def now():
    return DateTime.localtime()


def today():
    return now().date

def yesterday():
    yday = now() - a_day
    return yday.date

def parse(datetime_string, format):
    return DateTime.strptime(datetime_string, format)
