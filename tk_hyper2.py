# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 10:03:02 2019

@author: el_in
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Sep 08 11:50:37 2017
version 1.2

@author: Cgrs scripts
"""


import sys
import os
import os.path
import funciones_sismicas2 as fc
import json

PYTHON_VERSION = sys.version_info.major

PYTHON_VERSION

if PYTHON_VERSION < 3:
    try:
        import Tkinter as tk
    except ImportError:
        raise ImportError("Se requiere el modulo Tkinter")
else:
    try:
        import tkinter as tk
    except ImportError:
        raise ImportError("se requiere el modulo tkinter")
from tkinter import font

#################################################################################
## esta funcion genera el comentario y lo envia a la pagina, ademas de enviar
## los correos al sini automaticamente y la opcion de enviar correo a las partes
## interesadas.
##
## internaente necesita los archivos paths.txt de donde tomara las direcciones
## paths.txt tiene tres lineas:la primera de donde esta localizado el hyper.out
## la segunda  a donde enviara el dummyX.dat
## y la tercera a donde ira el dummyX.copy
##
## tambien tomara el archivo contactos.txt donde estaran los correos electroni
## cos de las partes interesadas, y contactos_sini.txt donde estaran los corre-
## os que se enviaran automaticamente al sini
##
################################################################################

def crear_hyper(formato,sentido,paths):

    '''
    # formato es el arreglo que contiene la informacion del sismo: latitud, longitud, comentario etc...
    # sentido es el valor dado al checkbox sentido para saber si el sismo fue sentido o no y publicarlo
    # en la pagina
    # paths es la variable que contiene las rutas necesarias para el programa
    '''
    '''aqui se crea el archivo en seisan con comentario'''
    fc.insertar_comentario(paths,formato,sentido)
    fc.guardar_datos(paths,formato)
    sentido = formato['sentido']
    if(bool_sini.get()):
        archivos_sini=open('contactos-sini.txt','r').readlines()
            #contactos_sini=['cramirez27@uasd.edu.do','cgrs27@gmail.com']#,'jleonel78@uasd.edu.do']

        contactos_sini=[]
        contactos_sini = [n[:-1] for n in archivos_sini if n not in contactos_sini]
        contactos_sini[-1]=archivos_sini[-1]
            #print(contactos_sini)
        fc.enviarEmail(contactos_sini,formato,sentido,paths)#si quieres en modo html anadir un tercer

        #esta parte envia los correos
        #destinatario =['cramirez27@uasd.edu.do','cgrs27@gmail.com']
        #destinatario =['cramirez27@uasd.edu.do','cgrs27@gmail.com','jleonel78@uasd.edu.do','amoreta78@uasd.edu.do']#,
                   #'sismos@sini.gob.do']
    if(bool_todos.get()):
        #argumento: 'html'
        archivos_contactos=open('contactos.txt','r').readlines()
        #contactos =['cramirez27@uasd.edu.do','cgrs27@gmail.com']#,'jleonel78@uasd.edu.do']
        #print(archivos_contactos[-1])
        contactos=[]
        contactos = [n[:-1] for n in archivos_contactos if n not in contactos]

        contactos[-1]=archivos_contactos[-1]
        fc.enviarEmail(contactos,formato,sentido,paths,'html')

    ch_sentido.deselect()
    sentido=False

def mensaje():
    if bool_sentido.get():
        sentido = True
        sentido_local = ' (Sentido).'
    else:
        sentido = False
        sentido_local = ''
    paths = open("paths.txt").readlines()
    path_poligonos = 'provinciascsv'
    path_ciudades = 'localidades_2mundo.dat'
    hyp_path = paths[0][:-1]#'hyp.out'#r'Z:\seismo\WOR\hyp.out'

    fpath = open(hyp_path)
    #lineas = fpath.readlines()
    #fpath.close()
    #fpath = open(hyp_path)
    #linea = fpath.readline()
    # para probar con lineas:
    # creamos lineas = fpath.realines()
    # para prueba comentaremos lineas de tal forma que a formatear_hyp
    # le llegue lineas en vez de linea, igual internamente formatear_hyp
    # tendra que crear una variable linea
    #fpath.close()

    ciudades = fc.get_ciudades(path_ciudades)
    # sustituimos linea por lineas para prueba
    formato = fc.formatear_hyp(fpath, path_poligonos,ciudades,sentido,mag_var.get())

    from tkinter import messagebox
    datos = formato['salida']+formato['comentario']+sentido_local
    # mensaje = f'{datos} \n\nEstas de acuerdo con los datos mostrados?'
    mensaje = '%s \n\nEstas de acuerdo con los datos mostrados?'%(datos)
    respuesta = messagebox.askyesno(message=mensaje,title='Validar Datos')
    if respuesta == True:
        crear_hyper(formato,sentido,paths)


#parte que crea la aplicacion grafica
root = tk.Tk()
root.title('Hyper')
root.geometry('540x320')
root.resizable(width=False, height=False)
font_size = font.Font(weight='bold',size=14)
mag_var = tk.IntVar()
bool_sini = tk.BooleanVar()
bool_todos = tk.BooleanVar()
bool_sentido = tk.BooleanVar()
backcolor='white smoke'
root.configure(background=backcolor)
#font_size=17
rbcoda = tk.Radiobutton(text="Mag Coda       ",background=backcolor,
                        font=font_size,variable=mag_var, value=1)
rblocal = tk.Radiobutton(text="Mag Local       ",background=backcolor,
                         font=font_size, variable=mag_var, value=2)
rbmw = tk.Radiobutton(text="Mag MW           ",background=backcolor,
                      font=font_size, variable=mag_var, value=3)
rbprom = tk.Radiobutton(text="Mag Promedio",background=backcolor,
                        font=font_size, variable=mag_var, value=4)

etiqueta = tk.Label(root,text='')
ch_correos = tk.Checkbutton(root,text='Enviar correos a SINI',background=backcolor,
                            font=font_size,variable=bool_sini)
ch_todos = tk.Checkbutton(root,text='Enviar correos a todos',
                          background=backcolor,font=font_size,variable=bool_todos)
etiqueta2 = tk.Label(root,text=' ')
boton = tk.Button(root,text='Enviar Datos',font=font_size,background='forest green',
                  foreground='yellow',command=mensaje)
ch_sentido = tk.Checkbutton(root,text='Sentido             ',font=font_size,background=backcolor,
                         variable=bool_sentido,foreground='red')
# etiqueta_status = tk.Label(root,text='Status:')
# status = tk.Label(root,text=var_status)
ch_correos.select()
etiqueta.grid(row=1,column=1)
rbcoda.grid(row=3,column=1)
rblocal.grid(row=2,column=1)
rbmw.grid(row=4,column=1)
rbprom.grid(row=5,column=1)
ch_sentido.grid(row=6,column=1)
ch_correos.grid(row=7,column=1)
ch_todos.grid(row=7,column=2)
etiqueta2.grid(row=8,column=1)
boton.grid(row=9,column=1)
# en un futuro se creara una etiqueta status donde se vera el status de la app
# etiqueta_status.grid(row=13,column=0)
# status.grid(row=13,column=1)

root.mainloop()
