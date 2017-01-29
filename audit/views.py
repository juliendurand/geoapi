from django.http import HttpResponse
from django.shortcuts import render

import src.audit


def index(request):
    address = src.audit.get_risk_audit('10 av jules ferry', '78500',
                                       'sartrouville')
    context = address.__dict__
    return render(request, 'audit/index.html', context)
