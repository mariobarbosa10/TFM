from django.contrib import admin
from django.urls import path,re_path,include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views
app_name = "modeloAprendizaje"

urlpatterns = [
    path('aprender', views.aprenderView, name='aprender'), 
    path('insumoBase', views.insumoBaseView, name='insumoBase'),  
    url(r'^aprendizaje$', views.aprendizaje, name='aprendizaje'),
    url(r'^insumoModificar$', views.modificarInsumoBase, name='insumoModificar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
