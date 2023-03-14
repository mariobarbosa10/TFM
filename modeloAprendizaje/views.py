import json
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render_to_response
from .utils import aprender, leerArchivoBase
import os
import pandas as pd

import os.path as path



pd.set_option('display.max_colwidth', 100000)

def aprenderView(request):
	context = {}
	return render(request, 'modeloAprendizaje/aprendizaje.html', context)

def aprendizaje(request):
	if request.method == 'POST':		  
		stop_words_path="./media/StopWords.txt"
		out_path=stop_words_df="./media/Diccionario_Palabras_Modelo.xlsx"
		palabras_compuestas_path="./media/Palabras_claves_compuestas_insumo.xlsx"
		uploaded_file = request.FILES["document"]		 
		filename = uploaded_file.name

		if os.path.exists('./media/' + filename):
			os.remove('./media/' + filename)

		if filename.endswith('.xlsx'):
			fs=FileSystemStorage()
			fs.save(uploaded_file.name,uploaded_file)
			entidades_path = "./media/" + filename
			excel_data = aprender(stop_words_path, entidades_path, out_path,palabras_compuestas_path)
			if excel_data=='0':
				os.remove('./media/' + uploaded_file.name)
				return render(request, 'modeloAprendizaje/aprendizaje.html', {"error":"Verifique los nombres de las columnas del archivo, descargar archivo ejemplo."})
		else:
			return render(request, 'modeloAprendizaje/aprendizaje.html', {"error":"No es un archivo con extensión .xlsx"})
		os.remove('./media/' + uploaded_file.name)
		return render(request, 'modeloAprendizaje/aprendizaje.html', {"excel_data":excel_data})
	else:
		return render(request, 'modeloAprendizaje/aprendizaje.html', {})

def insumoBaseView(request):
	archivo_palabras_clave="./media/Palabras_claves_compuestas_insumo.xlsx" 

	if path.exists(archivo_palabras_clave): 
		excel_data = leerArchivoBase(archivo_palabras_clave) 
		return render(request, 'modeloAprendizaje/insumoBase.html', {"excel_data":excel_data})
	else:
		return render(request, 'modeloAprendizaje/insumoBase.html', {"error":"No se encontró archivo base"})

def modificarInsumoBase(request):
	if request.method == 'POST':
		uploaded_file = request.FILES["document"]
		filename = uploaded_file.name 

		if filename.endswith('.xlsx'):
			filename = "base_insumo_db_system.xlsx"			 
			fs=FileSystemStorage()
			fs.save(filename ,uploaded_file)
			entidades_df=pd.read_excel("./media/" + filename)
			cont=0
			for a in (entidades_df.columns):
				if a=='Palabra_Clave':
					cont=cont+1
				elif a=='Entidad':
					cont=cont+1

			os.remove('./media/' + filename)
			if cont==2:
				nombre_base = "Palabras_claves_compuestas_insumo.xlsx"
				archivo_palabras_clave = "./media/" + nombre_base
				if path.exists(archivo_palabras_clave):
					os.remove(archivo_palabras_clave)
				fs=FileSystemStorage()
				fs.save(nombre_base ,uploaded_file)
				excel_data = leerArchivoBase(archivo_palabras_clave)
				return render(request, 'modeloAprendizaje/insumoBase.html', {"excel_data":excel_data})
			else:
				return render(request, 'modeloAprendizaje/insumoBase.html', {"error":"Verifique los nombres de las columnas del archivo, descargar archivo ejemplo."})
		else:
			return render(request, 'modeloAprendizaje/insumoBase.html', {"error":"No es un archivo con extensión .xlsx"})
	else:
		return render(request, 'modeloAprendizaje/insumoBase.html', {"error":"No se logró leer el archivo"})