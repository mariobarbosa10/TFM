
from django.contrib import admin
from django.urls import path,re_path,include
from django.conf.urls import url
from . import views
app_name = "modeloPredictivo"

urlpatterns = [ 
    path('predictivoManual', views.predictivoManual, name='predictivoManual'),  
    path('predictivoMasivo', views.predictivoMasivo, name='predictivoMsivo'),  
    url(r'^analizarManual$', views.analizar, name='modeloPredictivo.views.analizar'),
    url(r'^analizarMasivo$', views.analizarPredictivoMasivo, name='analizarMasivo'),
]
