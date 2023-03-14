
import nltk
import numpy as np
import nltk
import numpy as np
import spacy
nlp =  spacy.load('es_core_news_md', disable=["ner"])
from nltk.corpus import PlaintextCorpusReader
from scipy.stats import kurtosis
import pandas as pd
import time
import re
import os
hora_ini=time.strftime("%H:%M:%S")
pd.set_option('display.max_colwidth', 800000)


def main(dirname_path, stop_words_path, asunto):
    dirname_df=pd.read_excel(dirname_path)
    stop_words_df=pd.read_csv(stop_words_path, header=None)
    stop_words_df=stop_words_df.rename(columns={0:"Palabra"})
    dirname_df=dirname_df[["Palabra_Lema", "Entidad", "Peso", "Palabra_Base"]].drop_duplicates().rename(columns={"Palabra_Lema":"Palabra"})
    dirname_df=dirname_df[dirname_df["Palabra_Base"]==0]
    dirpalcomp_df=dirname_df[dirname_df["Palabra_Base"]==1]
    from nltk.corpus import stopwords
    stopwords = stopwords.words('spanish')
    stopwords_nltk_df=pd.DataFrame(stopwords)
    stopwords_nltk_df=stopwords_nltk_df.rename(columns={0:"Palabra"})
    stop_words_df=stop_words_df.append(stopwords_nltk_df)
    stop_words_df["Palabra"]=stop_words_df["Palabra"].apply(lambda x:x.upper())
    
    #Funcion para realizar lematizacion. 
    def lema_fun(x):
        word_lema = nlp(x.lower())
        for i in word_lema:
            return i.lemma_
    
    #Funcion para aplicar limpieza a cada uno de los documentos del corpus
    def custom_prepro(text):
        text=re.sub(r'\W+|\d+|_', ' ', text) #Removing numbers and punctuations
        textS=str(text)
        text=textS.upper()
        text=nltk.word_tokenize(text) 
        text=[lema_fun(word).upper() for word in text]
        return text
    
    #EVALUACION
    test_df=dirname_df.head(0)
    asunto=custom_prepro(asunto)
    for i in asunto:
        test_df=test_df.append(dirname_df[dirname_df['Palabra']==i.upper()],  ignore_index=True)
    salida_df=test_df.groupby(["Entidad"], as_index=False)["Peso"].sum().sort_values(by=['Peso'], ascending=False)
    salida_df["Prom"]=((salida_df["Peso"]*100)/salida_df["Peso"].sum())

    if(len(salida_df)>0):
            if(len(salida_df[salida_df["Prom"]>(np.percentile(round(salida_df.Prom), 25))])>6):
                salida_df=salida_df[salida_df["Prom"]>(np.percentile(round(salida_df.Prom), 25))].head(6) 
            else:
                salida_df=salida_df.head(6)

    salida_df["Prom"]=((salida_df["Peso"]*100)/salida_df["Peso"].sum())
    salida_df["Prom"]=salida_df["Prom"].map('{:,.2f}%'.format)
    arreglo=[]

    if(kurtosis(arreglo) < 0):
        def realiza_lema_compuesto(x):
            sentence = nlp(x.lower())
            palabra=""
            for word in sentence:
                if(len(stop_words_df[stop_words_df["Palabra"]==word.lemma_.upper()])==0):
                    palabra=palabra+" "+word.lemma_   
            return palabra.strip().upper()
        
        texto=realiza_lema_compuesto(str(entidades_df[entidades_df["codigo_peticion"]==codigo].asunto))
        for i,j in diccionario_insumo_manual_df.iterrows():
            if(dirpalcomp_df["Palabra_Lema"][i] in texto):
                acumula_df=acumula_df.append(diccionario_insumo_manual_df.iloc[i][["Palabra_Lema", "Entidad", "Peso"]])
                
        acumula_final_df=acumula_df.groupby(["Entidad"], as_index=False)["Peso"].sum().sort_values(by=['Peso'], ascending=False)
        acumula_final_df["Codigo_peticion"]=codigo
        salida_df=salida_df.append(acumula_final_df)
        salida_df["Prom"]=((salida_df["Peso"]*100)/salida_df["Peso"].sum())
        if(len(salida_df)>0):
            if(len(salida_df[salida_df["Prom"]>(np.percentile(round(salida_df.Prom), 25))])>6):
                salida_df=salida_df[salida_df["Prom"]>(np.percentile(round(salida_df.Prom), 25))].head(6) 
            else:
                salida_df=salida_df.head(6)
        return salida_df

    if(len(salida_df))<1:
            salida_df=salida_df.append({"Entidad":"SIN ENTIDAD RELACIONADA", "Prom": "0%"}, ignore_index=True)
    return salida_df[["Entidad", "Prom"]].reset_index(drop=True)

def analizar_text(text):
    dirname_path="./media/Diccionario_Palabras_Modelo.xlsx"
    stop_words_path="./media/StopWords.txt"
    asunto=text
    resultado = main(dirname_path,stop_words_path,asunto)
    resultado = resultado.to_json(orient='records')
    ret = {}
    ret['entities'] = resultado
    return ret

def mainMasivo(dirname_path, stop_words_path, input_path, output_path):
    dirname_df=pd.read_excel(dirname_path)
    entidades_df=pd.read_excel(input_path)
    
    cont=0
    for a in (entidades_df.columns):
        if a=='codigo_peticion':
            cont=cont+1
        elif a=='asunto':
            cont=cont+1       
         
    if cont==2:
        
        stop_words_df=pd.read_csv(stop_words_path, header=None)
        stop_words_df=stop_words_df.rename(columns={0:"Palabra"})
        dirname_df=dirname_df[["Palabra_Lema", "Entidad", "Peso", "Palabra_Base"]].drop_duplicates().rename(columns={"Palabra_Lema":"Palabra"})
        dirname_df=dirname_df[dirname_df['Palabra_Base']==0] #vahh
        dirpalcomp_df=dirname_df[dirname_df['Palabra_Base']==1] #vahh
        from nltk.corpus import stopwords
        stopwords = stopwords.words('spanish')
        stopwords_nltk_df=pd.DataFrame(stopwords)
        stopwords_nltk_df=stopwords_nltk_df.rename(columns={0:"Palabra"})
        stop_words_df=stop_words_df.append(stopwords_nltk_df)
        stop_words_df["Palabra"]=stop_words_df["Palabra"].apply(lambda x:x.upper())

        #Funcion para realizar lematizacion. 
        def lema_fun(x):
            word_lema = nlp(x.lower())
            for i in word_lema:
                return i.lemma_
        
        #Funcion para aplicar limpieza a cada uno de los documentos del corpus
        def custom_prepro(text):
            text=re.sub(r'\W+|\d+|_', ' ', text) #Removing numbers and punctuations
            textS=str(text)
            text=textS.upper()
            text=nltk.word_tokenize(text) 
            text=[lema_fun(word).upper() for word in text]
            return text

        # Recibe el codigo de la peticion y realiza los calculos para retornar un dataframe con toda la informacion. 
        def calculo_probabilidad(codigo):
            codigo_peticion=str(codigo)
            test_df=dirname_df.head(0)
            text=str(entidades_df[entidades_df["codigo_peticion"]==codigo].asunto)
            asunto=custom_prepro(text)

            for i in asunto:
                if(len(stop_words_df[stop_words_df["Palabra"]==i])<1):
                    test_df=test_df.append(dirname_df[dirname_df['Palabra']==i.upper()],  ignore_index=True)

            salida_df=test_df.groupby(["Entidad"], as_index=False)["Peso"].sum().sort_values(by=['Peso'], ascending=False)
            salida_df["Codigo_peticion"]=codigo
            salida_df["Prom"]=((salida_df["Peso"]*100)/salida_df["Peso"].sum())

            if(len(salida_df)>0):
                if(len(salida_df[salida_df["Prom"]>(np.percentile(round(salida_df.Prom), 25))])>6):
                    salida_df=salida_df[salida_df["Prom"]>(np.percentile(round(salida_df.Prom), 25))].head(6) 
                else:
                    salida_df=salida_df.head(6)

            salida_df["Prom"]=((salida_df["Peso"]*100)/salida_df["Peso"].sum())
            salida_df["Prom"]=salida_df["Prom"].map('{:,.2f}%'.format)
            salida_df.reset_index(drop=True) # hasta aca retornaba la funcion
            arreglo=[]
            salida_df["Peso"].apply(lambda x:arreglo.append(x))
            acumula_df=pd.DataFrame(columns=("Palabra_Clave", "Entidad", "Peso"))

            if(kurtosis(arreglo) < 0):
                def realiza_lema_compuesto(x):
                    sentence = nlp(x.lower())
                    palabra=""
                    for word in sentence:
                        if(len(stop_words_df[stop_words_df["Palabra"]==word.lemma_.upper()])==0):
                            palabra=palabra+" "+word.lemma_   
                    return palabra.strip().upper()
                
                texto=realiza_lema_compuesto(str(entidades_df[entidades_df["codigo_peticion"]==codigo].asunto))
                for i,j in dirpalcomp_df.iterrows():
                    if(dirpalcomp_df["Palabra_Clave"][i] in texto):
                        acumula_df=acumula_df.append(dirpalcomp_df.iloc[i][["Palabra_Clave", "Entidad", "Peso"]])
                
                acumula_final_df=acumula_df.groupby(["Entidad"], as_index=False)["Peso"].sum().sort_values(by=['Peso'], ascending=False)
                acumula_final_df["Codigo_peticion"]=codigo
                salida_df=salida_df.append(acumula_final_df)
            
            salida_df["Prom"]=((salida_df["Peso"]*100)/salida_df["Peso"].sum())
           
            if(len(salida_df)>0):
                if(len(salida_df[salida_df["Prom"]>(np.percentile(round(salida_df.Prom), 25))])>6):
                    salida_df=salida_df[salida_df["Prom"]>(np.percentile(round(salida_df.Prom), 25))].head(6) 
                else:
                    salida_df=salida_df.head(6)

            salida_df["Prom"]=salida_df["Prom"].map('{:,.2f}%'.format)        
            return salida_df

    
        salida_df=pd.DataFrame(columns=('Entidad', 'sum')) #Crea o Limpia el DataFrame
        #Llamado a la funcion calculo_probabilidad por cada peticion.
        for indice_fila, fila in entidades_df.iterrows():
            salida_df=salida_df.append(calculo_probabilidad(entidades_df.codigo_peticion[indice_fila]))
            #print(str(indice_fila)+" "+time.strftime("%H:%M:%S"))
        salida_df=salida_df[["Codigo_peticion", "Entidad", "Peso", "Prom"]]
        salida_df=salida_df.drop_duplicates()
        salida_df.sort_values(by=['Codigo_peticion', 'Peso'], ascending=False)
        salida_df.to_excel(output_path)
        
        #parte de leer el archivo y mostrarlo en pantalla   
        df_aprendizaje=pd.read_excel(output_path)
        df_aprendizaje=df_aprendizaje[["Codigo_peticion", "Entidad","Prom"]].reset_index(drop=True)
        
        excel_data = list()
        for row in df_aprendizaje.itertuples(index=False, name='Pandas'):
            row_data = list()
            for cell in row:
                row_data.append(str(cell))
            excel_data.append(row_data)
        os.remove(output_path)
        return excel_data
    else:
        return '0'

def analizar_masivo(filename):
    dirname_path="./media/Diccionario_Palabras_Modelo.xlsx"
    stop_words_path="./media/StopWords.txt"
    input_path="./media/" + filename
    output_path="./media/salida_prediccion.xlsx"
    resultado = mainMasivo(dirname_path, stop_words_path, input_path, output_path)    
    return resultado
