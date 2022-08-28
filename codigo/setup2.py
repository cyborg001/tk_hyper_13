# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 23:06:18 2018
tk_hyper version 8
ahora escribe el comentario automaticamente a la base
de datos en REA seisan
@author: el_in, cgrs27 Carlos Ramirez
bdist_msi
"""

import cx_Freeze
import sys
import os
base = None

if sys.platform == 'win32':
    base = 'Win32GUI'
directorio = os.getcwd()
executables = [cx_Freeze.Executable(os.path.join(directorio,"tk_hyper2.py"),base=base)]

#r'C:\Users\el_in\OneDrive\Documentos\carlos\sismologico programas\dummier4\tk_Dummier.py'

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

cx_Freeze.setup(
    name = "Hyper 9",
    options = {"build_exe":{"packages":["tkinter","email","smtplib",'os'],
                            "include_files":[os.path.join(directorio,"funciones_sismicas2.py"),
                                             os.path.join(directorio,"tk_hyper2.py"),
                                             os.path.join(directorio,"hyp.out"),
                                             os.path.join(directorio,"contactos.txt"),
                                             os.path.join(directorio,"contactos-sini.txt"),
                                             os.path.join(directorio,"localidades_2mundo.dat"),
                                             os.path.join(directorio,"paths.txt"),
                                             os.path.join(directorio,"provinciascsv"),
                                             os.path.join(directorio,"setup2.py"),
											 os.path.join(directorio,"equake.ico"),
                                             os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
                                             os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
                                             ]},
                'bdist_msi': {
                    'add_to_path': True,
                    # 'environment_variables': [
                    #     ("E_MYAPP_VAR", "=-*MYAPP_VAR", "1", "TARGETDIR")
                    # ],
                    # 'install_icon':r"C:\hiper8\tk_hyper_8equake.ico",
                    }},
    version = "9.1.0",
    description = "Programa que localiza la ciudad donde ocurre el evento sismico y envia la informacion por correo",
    executables = executables,


    )
