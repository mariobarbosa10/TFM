import json
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from .utils import analizar_text, analizar_masivo
from django.shortcuts import render_to_response
from django.core.files.storage import FileSystemStorage
import os
import openpyxl

#############
from django.views.generic import(
    TemplateView,
    ListView,
    CreateView,
)
 



##############
if settings.ALLOW_URL_IMPORTS:
    import requests
    from bs4 import BeautifulSoup
    from readability import Document

def predictivoManual(request):
    return render(request, 'modeloPredictivo/predictivoManual.html', {})

def analizar(request):
    'API text analyze view'
    if request.method == 'POST':
        text = request.body.decode('utf-8')
        try:
            text = json.loads(text)['text']
        except ValueError:
            # catch POST form as well
            for key in request.POST.dict().keys():
                text = key
 
        if not text:
            response = JsonResponse(
                {'status': 'false', 'message': 'need some text here!'})
            response.status_code = 400
            return response 

        text = text[:200000]
        ret = {}
        ret = analizar_text(text)
        return JsonResponse(ret)
    else:
        ret = {'methods_allowed': 'POST'}
        return JsonResponse(ret)

def predictivoMasivo(request):
    return render(request, 'modeloPredictivo/predictivoMasivo.html', {})

def analizarPredictivoMasivo(request):
    if request.method == 'POST':    
        uploaded_file = request.FILES["document"]   
        filename = uploaded_file.name 
        
        if os.path.exists('./media/' + filename):
                os.remove('./media/' + filename)
        
        if filename.endswith('.xlsx'): 
            fs=FileSystemStorage()
            fs.save(uploaded_file.name,uploaded_file)
            excel_data = analizar_masivo(filename)
            if excel_data=='0':
                os.remove('./media/' + filename)
                return render(request, 'modeloPredictivo/predictivoMasivo.html', {"error":"Verifique los nombres de las columnas del archivo, descargar archivo ejemplo."})
        else:
            return render(request, 'modeloPredictivo/predictivoMasivo.html', {"error":"No es un archivo con extensión .xlsx"})
        os.remove('./media/' + filename)
        return render(request, 'modeloPredictivo/predictivoMasivo.html', {"excel_data":excel_data})
    else:
        return render(request, 'modeloPredictivo/predictivoMasivo.html', {})
 
 