#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string
#Se importa los modulos necesarios de pdfminer

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

import re

def convertir(archivo, paginas=None):
    #Si no se le pasa el numero de paginas se inicializa pagenums si no se le pasa 
    #a pagenums el numero de paginas.
    if not paginas:
        pagenums = set()
    else:
        pagenums = set(paginas)

    #Se define la salida
    output = StringIO()
    #Se crea la instancia del manejador
    manager = PDFResourceManager()
    #se instancia el conversor de texto donde se le pasa el manejador y la salida
    converter = TextConverter(manager, output, laparams=LAParams())
    #Se instancia el interprete pasando el manejador y el conversor
    interpreter = PDFPageInterpreter(manager, converter)

    #Se abre el archivo de entrada
    infile = file(archivo, 'rb')
    #Se crea un ciclo pasando el archivo de entrada y el numero de paginas.
    for page in PDFPage.get_pages(infile, pagenums):
        #Se procesa cada pagina
        interpreter.process_page(page)
    #Se cierra el archivo de entrada
    infile.close()
    #Se cierra el conversor
    converter.close()
    #Se obtiene los valores de la salida en texto
    texto = output.getvalue()
    #Se cierra la salida
    output.close
    #Se devuelve el texto
    resultado = string.split(texto,"\n")

    return resultado

def extraerDatos(archivo):
    listado = convertir(archivo)
    patron_rif = re.compile(r"(J-\d+)")
    #patron_ = re.compile()
    patron_numero = re.compile(r"(\d+)")
    pattern = re.compile(r"(\d+)")

    lista = []
    for i in listado: 
        resultado_numero=  patron_numero.findall(i)
        if (len(resultado_numero) == 1) and (len(resultado_numero[0]) <= 3):
            nombre = i.split(" ")[1:]
            nombre = string.join(nombre," ")
            lista.append({'numero': int(resultado_numero[0]),"empresa": nombre})
    
    contador = { "rif": 1, "monto":1}

    for i in listado:
        resultado_rif = patron_rif.findall(i)
        if len(resultado_rif) <> 0:
            for num in range(len(lista)):
                if  (lista[num]["numero"] == contador["rif"]):
                    lista[num]["rif"] = resultado_rif[0]
                    break
            contador["rif"] = contador["rif"] + 1
        if (string.find(i,",") <> -1 and len(i.split(" ")) == 1):
            for num in range(len(lista)):
                if  (lista[num]["numero"] == contador["monto"]):
                    lista[num]["monto"] = i
                    break
            contador["monto"] = contador["monto"] +1

    return lista



if __name__ == "__main__":
    import pymongo
    connection = pymongo.MongoClient("mongodb://localhost")
    db=connection.cencoex
    salud = db.salud

    datos = extraerDatos("salud.pdf")
    for num in range(len(datos)):
        if len(datos[num].keys()) == 4:
            try:
                salud.insert_one(datos[num])
            except Exception as e:
                print "Unexpected error:", type(e), e


