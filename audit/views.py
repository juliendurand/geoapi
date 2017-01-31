from django.http import HttpResponse
from django.shortcuts import render

import src.audit


def index(request):
    address = request.GET.get('address')
    zipcode = request.GET.get('zip')
    city = request.GET.get('city')

    result = src.audit.get_risk_audit(address, zipcode, city)
    print(result.to_json())
    risks = result.__dict__['risks']
    for risk in risks:
        risk['cursor'] = int(risk['ratio'] * 200 - 5)
    context = result.__dict__
    return render(request, 'audit/index.html', context)
