from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

import json
from .models import Currency, ExchangeRate


def index(request):
    return HttpResponse("Hello, this is the currency converter.")

@csrf_exempt
@require_http_methods(["POST"])
def convert_currency(request):

    try:
        data = json.loads(request.body)
        base_currency = data.get('base_currency')
        target_currency = data.get('target_currency')
        date = data.get('date')

        # ORM
        exchange_rate = ExchangeRate.objects.get(
            base_currency__code=base_currency,
            target_currency__code=target_currency,
            date=date
        )

        return JsonResponse({
            'base_currency': base_currency,
            'target_currency': target_currency,
            'date': date,
            'rate': float(exchange_rate.rate)
        })

    except ExchangeRate.DoesNotExist:
        return JsonResponse({
            'error': 'Exchange rate not found for the specified currencies and date'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)