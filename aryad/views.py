import requests
from django.http import JsonResponse

def get_geo(request):
    # Récupérer la vraie IP du visiteur (derrière Nginx)
    ip = (
        request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
        or request.META.get('REMOTE_ADDR')
    )

    try:
        response = requests.get(
            f'http://ip-api.com/json/{ip}?fields=status,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting',
            timeout=4,
            headers={'User-Agent': 'aryadstudio.com'}
        )
        response.raise_for_status()
        data = response.json()

        if data.get('status') != 'success':
            return JsonResponse({}, status=204)

        return JsonResponse({
            # Géo
            'country_name': data.get('country', ''),
            'country_code': data.get('countryCode', ''),
            'region':       data.get('regionName', ''),
            'region_code':  data.get('region', ''),
            'city':         data.get('city', ''),
            'zip':          data.get('zip', ''),
            'latitude':     data.get('lat'),
            'longitude':    data.get('lon'),
            'timezone':     data.get('timezone', ''),
            # Réseau
            'isp':          data.get('isp', ''),
            'org':          data.get('org', ''),
            'as':           data.get('as', ''),
            # Flags utiles
            'is_mobile':    data.get('mobile', False),
            'is_proxy':     data.get('proxy', False),
            'is_hosting':   data.get('hosting', False),
        })
    except requests.exceptions.Timeout:
        return JsonResponse({}, status=204)
    except requests.exceptions.RequestException:
        return JsonResponse({}, status=204)