import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def get_geo(request):
    try:
        response = requests.get(
            'https://ipapi.co/json/',
            timeout=4,
            headers={'User-Agent': 'aryadstudio.com'}
        )
        response.raise_for_status()
        data = response.json()
        return JsonResponse({
            'country_name': data.get('country_name', ''),
            'country_code': data.get('country_code', ''),
            'city':         data.get('city', ''),
            'region':       data.get('region', ''),
            'latitude':     data.get('latitude'),
            'longitude':    data.get('longitude'),
        })
    except requests.exceptions.Timeout:
        return JsonResponse({}, status=204)
    except requests.exceptions.RequestException:
        return JsonResponse({}, status=204)