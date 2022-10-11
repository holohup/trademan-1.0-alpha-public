from django.core.management import call_command
from datetime import datetime


def daily_updater(get_response):
    date = datetime.now().date()

    def middleware(request):
        nonlocal date
        current_date = datetime.now().date()
        if request.method == 'GET' and current_date != date:
            try:
                result = call_command('update')
            except Exception as error:
                print(f'Could not update prices! {error}')
                raise error
            else:
                print(f'\nFigis updated from TCS. Result:\n{result}')
                date = current_date
        response = get_response(request)

        return response

    return middleware


