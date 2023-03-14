
import pandas as pd
import numpy as np
import nltk
import time
import spacy



nlp =  spacy.load('es_core_news_sm', disable=["ner"])#Cambiar a ner
pd.set_option('display.max_colwidth', 100000)


def aprender(stop_words_path, entidades_path, out_path,palabras_compuestas_path):
    
    stop_words_df=pd.read_csv(stop_words_path, header=None)
    entidades_df=pd.read_excel(entidades_path)
    
    
    cont=0
    for a in (entidades_df.columns):
        if a=='codigo_peticion':
            cont=cont+1
        elif a=='asunto':
            cont=cont+1
        elif a=='nombre_entidad':     
            cont=cont+1

    if cont==3:

        palabras_compuestas_df=pd.read_excel(palabras_compuestas_path)
        cantidad_peticiones_df=entidades_df[["nombre_entidad", "codigo_peticion"]].groupby(["nombre_entidad"], as_index=False).agg("count")
    
        entidades_df["asunto"]=entidades_df["asunto"].apply(lambda x:str(x).upper())
    
        ent_unique=entidades_df["nombre_entidad"].unique()
        entidad_final_df=pd.DataFrame(columns=("Palabra", "Conteo", "Entidad"))
        stop_words_df=stop_words_df.rename(columns={0:"Palabra"})
          
        import re
        from nltk.corpus import stopwords

        stopwords = stopwords.words('spanish')
        stopwords_nltk_df=pd.DataFrame(stopwords)
        stopwords_nltk_df=stopwords_nltk_df.rename(columns={0:"Palabra"})
        stop_words_df=stop_words_df.append(stopwords_nltk_df)
        stop_words_df["Palabra"]=stop_words_df["Palabra"].apply(lambda x:x.upper())

        #Funcion para aplicar limpieza a cada uno de los documentos del corpus
        def custom_prepro(text):
            text=str(text)
            text=re.sub(r'\W+|\d+|_', ' ', text) #Removing numbers and punctuations
            textS=str(text)
            text=textS.upper()
            text=nltk.word_tokenize(text) #Tokenizacion
            return text

        def fun_all_words(entidad_clean):
            cont=0
            for x in entidad_clean:
                for t in entidad_clean[cont]:
                    all_words.append(t.replace("'","").replace(",","").replace("[","").replace("]",""))
                cont=cont+1
         
        def final(all_words,entidad):
            all_words_final= nltk.FreqDist(all_words)
            final_list =all_words_final.most_common(250)
            final_df=pd.DataFrame(final_list)
            final_df["Entidad"]=entidad
            final_df=final_df.rename(columns = {0:"Palabra", 1:"Conteo"})
            return final_df
        
        #Llamado a funcion y se crea el dataFrame entidad_final_df que almacena todas las palabras que no estan como stopwords
         
        for i in ent_unique:
            entidad=entidades_df[entidades_df["nombre_entidad"]==i]
            entidad_clean=(entidad["asunto"].apply(lambda x:custom_prepro(x)))
            text=[]
            for my_var in entidad_clean:
                palabra=str(my_var)
                palabra=palabra.upper()
                word_tokens = nltk.word_tokenize(palabra)
                for w in word_tokens:
                    text.append(w)
            entidad_clean=pd.DataFrame(text)
            entidad_clean=entidad_clean.reset_index(drop=True)
            all_words=[]
            fun_all_words(entidad_clean)
            entidad_final_df=entidad_final_df.append(final(all_words,i), ignore_index=True)
        entidad_final_df=entidad_final_df.rename(columns = {0:"Palabra", 1:"Conteo"})
        entidad_final_df=entidad_final_df[entidad_final_df["Palabra"]!=""]
          
        #Funcion para realizar lematizacion. 
        def lema_fun(x):
            word_lema = nlp(x.lower())
            for i in word_lema:
                return i.lemma_
        
        #Crear columna Palabra_Lema y llamar la funcion lema_fun para hacer la lematizacion de todo el data frame. 
        hora_ini=time.strftime("%H:%M:%S")
        entidad_final_df["Palabra_Lema"]=""
        entidad_final_df["Palabra_Lema"]=entidad_final_df["Palabra"].apply(lambda x:lema_fun(x).upper())
         
        #Luego de que tenemos lematizado se realiza validacion contra StopWords para quitar las palabras.         
        for i, j in entidad_final_df.iterrows():
            if(len(stop_words_df[(stop_words_df["Palabra"]==entidad_final_df["Palabra_Lema"][i]) | (stop_words_df["Palabra"]==entidad_final_df["Palabra"][i])])>0) or (len(entidad_final_df["Palabra"][i])<3):
                entidad_final_df=entidad_final_df.drop([i], axis=0)
        entidad_final_df=entidad_final_df.reset_index(drop=True)
         
        #Crear dataframe total_df para agrupar y sumar la frecuencia de las palabras por entidad y por palabra lema. 
        total_df=entidad_final_df.groupby(["Entidad", "Palabra_Lema"], as_index=False)["Conteo"].sum()
        
        #Se realiza cruce entre entidad_final_df y total_df para añadir al primer dataframe el conteo total de esa palabra lematizada por esa entidad. 
        entidad_final_df=entidad_final_df.merge(total_df, how="inner", on=["Palabra_Lema","Entidad"])[["Palabra", "Palabra_Lema","Entidad","Conteo_x","Conteo_y"]].rename(columns={"Conteo_y":"Conteo_Total"})
        
        entidad_final_df["Cantidad"]=""
        def cuenta_palabras_total_df(palabra):
            conteo=len(entidades_df[(entidades_df["asunto"].str.contains(palabra)==True)]["codigo_peticion"].unique())
            return conteo
     
        entidad_final_df["Cantidad"]=entidad_final_df["Palabra"].apply(lambda x:cuenta_palabras_total_df(x))         
        entidad_final_df.head()
        
        #Calculo de promedio de conteo de palabras y retorna un dataFrame con esa nueva columna, donde el 100% es la ocurrencia maxima.
        def promedio(Conteo, entidad, palabra_original, q1):
            if(cantidad_peticiones_df[cantidad_peticiones_df["nombre_entidad"]==entidad]["codigo_peticion"]<=q1).bool(): #IF PARA VALIDAR SI LA CANTIDAD DE PETICIONES ES MENOR AL CUARTIL 1 DE LA CANTIDAD DE PETICIONES. 
                word=len(entidades_df[entidades_df["nombre_entidad"]==entidad]["codigo_peticion"].unique())
            else:
                word=entidad_final_df[(entidad_final_df["Palabra"]==palabra_original) & (entidad_final_df["Entidad"]==entidad)]["Cantidad"].astype(int)
            word_ent=len(entidades_df[(entidades_df["asunto"].str.contains(palabra_original)==True) & (entidades_df["nombre_entidad"]==entidad)]["codigo_peticion"].unique())
            promedio2=(word_ent*100)/word
            return promedio2
        
        #Poblar el campo Promedio para cada registro en el DF entidad_final\nhora_ini=time.strftime("%H:%M:%S") 
        entidad_final_df["Promedio"]=0
        q1=np.percentile(cantidad_peticiones_df.codigo_peticion, 25)
        entidad_final_df["Promedio"]=entidad_final_df.apply(lambda x: float(promedio(x.Conteo_Total, x.Entidad, x.Palabra, q1)), axis=1)
         
        
        prom_unif_df=entidad_final_df.groupby(["Palabra_Lema", "Entidad"], as_index=False)["Promedio"].max()
        def unifica_prom(palabra, entidad):
            return int(prom_unif_df[(prom_unif_df["Palabra_Lema"]==palabra) & (prom_unif_df["Entidad"]==entidad)].Promedio)
        
        entidad_final_df["Promedio"]=entidad_final_df.apply(lambda x: unifica_prom(x.Palabra_Lema, x.Entidad), axis=1)#[["Palabra", "Entidad"]].apply(lambda x:unifica_prom(x,y))
           
        #Funcion para construir el diccionario_df seleccionando unicamente las mejores palabras por cada entidad. 
        def hacer_diccionario(diccionario_df):
            for i in ent_unique:
                temporal_df=entidad_final_df[entidad_final_df["Entidad"]==i]
                if(len(temporal_df)>150):
                    temporal_df=temporal_df.sort_values(["Promedio"], ascending=False).head(150)
                    if(temporal_df.Promedio.min()<15):
                        diccionario_df=diccionario_df.append(temporal_df.head(150), ignore_index=True)    
                    else:
                        diccionario_df=diccionario_df.append(temporal_df[temporal_df["Promedio"]>temporal_df["Promedio"].mean()], ignore_index=True)
                else:
                    diccionario_df=diccionario_df.append(temporal_df[temporal_df["Promedio"]>15], ignore_index=True) #EL 20 ES EL QUE SE MUEVE
            return diccionario_df
           
        diccionario_df=pd.DataFrame(columns=("Palabra", "Palabra_Lema", "Entidad"), dtype=int)
        diccionario_df=hacer_diccionario(diccionario_df)
                   
        def calcular_peso (indice, palabra, entidad, diez, veinte):
            promedio_aux=pd.DataFrame(diccionario_df.groupby(["Entidad"], as_index=False)["Promedio"].mean())
            tercer_df=diccionario_df[(diccionario_df["Palabra_Lema"]==palabra) & (diccionario_df["Promedio"]>15)]
            if((int(len(tercer_df.groupby(["Palabra_Lema", "Entidad"]).mean())<=diez)) & (int(len(tercer_df[tercer_df["Entidad"]==entidad]))>=1)):
                if(int(len(diccionario_df[diccionario_df["Palabra_Lema"]==palabra].groupby(["Palabra_Lema", "Entidad"]).mean())<2)):
                    if(float(diccionario_df[diccionario_df.index==indice].Promedio) >= float(promedio_aux[promedio_aux["Entidad"]==entidad].Promedio)):
                        peso=3
                    else:
                        peso=2
                elif (int(len(diccionario_df[diccionario_df["Palabra_Lema"]==palabra].groupby(["Palabra_Lema", "Entidad"]).mean())<veinte)):
                    if(float(diccionario_df[diccionario_df.index==indice].Promedio) >= float(promedio_aux[promedio_aux["Entidad"]==entidad].Promedio)):
                        peso=2
                    else:
                        peso=1
                else:
                    peso=0
            elif ((float(diccionario_df[diccionario_df.index==indice].Promedio) >= float(promedio_aux[promedio_aux["Entidad"]==entidad].Promedio)) & int(len(tercer_df.groupby(["Palabra_Lema", "Entidad"]).mean())<= veinte) & (int(len(tercer_df[tercer_df["Entidad"]==entidad]))>=1)):
                peso=2 #Validar precision del modelo con dos.
            elif((len(entidad_final_df[(entidad_final_df["Palabra_Lema"] == palabra) & (entidad_final_df["Promedio"] > 25)]) < veinte)):
                peso=1
            else:
                peso=0
            return peso
         
        def calculo_min_entidades (indice, palabra, entidad, diez):
            promedio_aux=pd.DataFrame(diccionario_df.groupby(["Entidad"], as_index=False)["Promedio"].mean())
            tercer_df=diccionario_df[(diccionario_df["Palabra_Lema"]==palabra) & (diccionario_df["Promedio"]>15)]
            if((int(len(tercer_df.groupby(["Palabra_Lema", "Entidad"]).mean())<=diez)) & (int(len(tercer_df[tercer_df["Entidad"]==entidad]))>=1)):
                if(float(diccionario_df[diccionario_df.index==indice].Promedio) >= float(promedio_aux[promedio_aux["Entidad"]==entidad].Promedio)):
                    peso=3
                else:
                    peso=2
            elif ((float(diccionario_df[diccionario_df.index==indice].Promedio) >= float(promedio_aux[promedio_aux["Entidad"]==entidad].Promedio)) & (int(len(tercer_df[tercer_df["Entidad"]==entidad]))>=1)):
                peso=1
            else:
                peso=0
            return peso       
        
        diccionario_df["Peso"]=""
        total=len(ent_unique)
        if (len(ent_unique) > 10):
            uno=(11.5*total)/100
            dos=(20*total)/100
            for indice_fila, fila in diccionario_df.iterrows():
                diccionario_df["Peso"][indice_fila]=calcular_peso(indice_fila,diccionario_df["Palabra_Lema"][indice_fila],diccionario_df["Entidad"][indice_fila], uno, dos)
        else:
            uno=(50*total)/100
            for indice_fila, fila in diccionario_df.iterrows():
                diccionario_df["Peso"][indice_fila]=calculo_min_entidades(indice_fila,diccionario_df["Palabra_Lema"][indice_fila],diccionario_df["Entidad"][indice_fila], uno)
         
        diccionario_final=diccionario_df
        diccionario_final=diccionario_final[diccionario_final["Peso"]>0]
        diccionario_final=diccionario_final.rename(columns = {"Palabra":"Palabra_original"})[["Palabra_original", "Palabra_Lema", "Entidad", "Peso"]].sort_values(["Entidad", "Peso", "Palabra_Lema"], ascending=True).reset_index(drop=True)
        diccionario_final["Palabra_Base"]="0"
        
        ########################## Inicio Tratamiento insumo 2 ###########

        #Nueva funcion que realiza lematizacion y stopwords a frases y no a palabras. 
        def realiza_lema_compuesto(x):
            sentence = nlp(x.lower())
            palabra=""
            for word in sentence:
                if(len(stop_words_df[stop_words_df["Palabra"]==word.lemma_.upper()])==0):
                    palabra=palabra+" "+word.lemma_   
            return palabra.strip().upper()

        def calcula_peso_compuesta(Palabra):
                cantidad=len(palabras_compuestas_df[palabras_compuestas_df["Palabra_Lema"]==Palabra])
                if(cantidad==1):
                    if(Palabra.count(" ")>=2):
                        peso=6
                    elif(Palabra.count(" ")==1):
                        peso=5
                    else:
                        peso=4
                elif(cantidad<3):
                    if(Palabra.count(" ")>=2):
                        peso=5
                    elif(Palabra.count(" ")==1):
                        peso=4
                    else:
                        peso=3
                elif(cantidad<7):
                    if(Palabra.count(" ")>=2):
                        peso=3
                    elif(Palabra.count(" ")==1):
                        peso=2
                    else:
                        peso=1
                else:
                    peso=0
                return peso
        
        palabras_compuestas_df["Palabra_Lema"]=palabras_compuestas_df["Palabra_Clave"].apply(lambda x:realiza_lema_compuesto(x))
        palabras_compuestas_df=palabras_compuestas_df[palabras_compuestas_df["Palabra_Lema"]!='']

        #Hacemos inner join con el diccionario para no repetir las mismas palabras del aprendizaje y del segundo insumo
        palabras_borrar_df=palabras_compuestas_df.merge(diccionario_final, 
                             how="inner", 
                             left_on=["Palabra_Lema", "Entidad"], 
                             right_on=["Palabra_Lema", "Entidad"]
                            )[["Palabra_Clave", "Entidad"]].drop_duplicates()

        for i, j in palabras_compuestas_df.iterrows():
            if(len(palabras_borrar_df[palabras_borrar_df["Palabra_Clave"]==palabras_compuestas_df["Palabra_Lema"][i]])>0):
                palabras_compuestas_df=palabras_compuestas_df.drop([i], axis=0)
        palabras_compuestas_df=palabras_compuestas_df.reset_index(drop=True)

        palabras_compuestas_df["Peso"]=""
        palabras_compuestas_df["Palabra_Base"]="1"

        palabras_compuestas_df["Peso"]=""
        palabras_compuestas_df["Peso"]=palabras_compuestas_df["Palabra_Lema"].apply(lambda x:calcula_peso_compuesta(x))
        palabras_compuestas_df=palabras_compuestas_df[palabras_compuestas_df["Peso"]>0]

        #palabras_compuestas_df.to_excel("./media/aprender/Diccionario_Palabras_Compuestas.xlsx", index=False) # se genrea interno para el programa
     
        sequence = ['Palabra_Clave','Palabra_Lema','Entidad','Peso','Palabra_Base']
    
        palabras_compuestas_df = palabras_compuestas_df.reindex(columns=sequence)
        palabras_compuestas_df = palabras_compuestas_df.rename(columns={"Palabra_Clave":"Palabra_original"})
        
        Archivo_final_df = pd.concat([diccionario_final,palabras_compuestas_df], axis=0) # diccionario_final.merge(palabras_compuestas_df)
        Archivo_final_df.to_excel(out_path)

        #leer el resultado para mostrar en pantalla 
        archivo_palabras_clave="./media/Diccionario_Palabras_Modelo.xlsx"
        df_aprendizaje=pd.read_excel(archivo_palabras_clave)
        df_aprendizaje=df_aprendizaje[["Palabra_original", "Palabra_Lema","Entidad"]].reset_index(drop=True)
        
        excel_data = list()
        
        for row in df_aprendizaje.itertuples(index=False, name='Pandas'):
            row_data = list()
            for cell in row:
                row_data.append(str(cell))
            excel_data.append(row_data)
        return excel_data
    else:
        return '0'
    
    

def leerArchivoBase(archivo_palabras_clave):
    df_aprendizaje=pd.read_excel(archivo_palabras_clave)
    df_aprendizaje=df_aprendizaje[["Palabra_Clave", "Entidad"]].reset_index(drop=True)
    excel_data = list()

    for row in df_aprendizaje.itertuples(index=False, name='Pandas'):
        row_data = list()
        for cell in row:
            row_data.append(str(cell))
        excel_data.append(row_data)
    return excel_data