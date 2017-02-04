from django.shortcuts import redirect, render, reverse

import src.audit


def index(request):
    address = request.GET.get('address', '')
    zipcode = request.GET.get('zip', '')
    city = request.GET.get('city', '')
    context = {
        'address': address,
        'zipcode': zipcode,
        'city': city,
    }
    return render(request, 'audit/index.html', context)


def result(request):
    address = request.GET.get('address')
    zipcode = request.GET.get('zip')
    city = request.GET.get('city')

    if address and zipcode and city:
        result = src.audit.get_risk_audit(address, zipcode, city)
        if result:
            risks = result.__dict__['risks']
            for risk in risks:
                risk['cursor'] = int(risk['ratio'] * 200 - 5)
            context = result.__dict__
            #print(result.to_json())
            return render(request, 'audit/result.html', context)

    return redirect(reverse('index') + '?' + request.GET.urlencode())
