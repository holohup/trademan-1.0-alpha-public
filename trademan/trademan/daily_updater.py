from datetime import datetime

from django.core.management import call_command


def daily_updater(get_response):
    date = datetime.now().date()

    def middleware(request):
        nonlocal date
        current_date = datetime.now().date()
        if request.method == 'GET' and current_date != date:
            try:
                call_command('update')
            except Exception as error:
                print(f'Could not update prices! {error}')
                raise error
            else:
                date = current_date
        return get_response(request)

    return middleware
