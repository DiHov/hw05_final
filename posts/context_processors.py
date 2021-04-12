import datetime as dt


def year(request):
    date = dt.datetime.now().year
    return {'year': date}
