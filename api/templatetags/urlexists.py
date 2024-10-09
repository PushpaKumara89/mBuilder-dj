from django.template.defaultfilters import register
import urllib3


@register.filter('urlexists')
def urlexists(url):
    try:
        with urllib3.PoolManager() as http:
            print('->>>>>>>>>>>>>>>>>>>>')
            print(url)
            print('<<<<<<<<<<<<<<<<<<<<-')
            response = http.request('HEAD', url)
            print('--------')
            print(response.status)
            print('--------')
            return response.status == 200
    except Exception as exception:
        print('--------')
        print(exception)
        print('--------')
        return False

