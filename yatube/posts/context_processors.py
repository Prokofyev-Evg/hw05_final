import datetime as dt


def year(request):
    '''
    Добавляет переменную с текущим годом.
    '''
    return {
        'YEAR': dt.datetime.today().year
    }
