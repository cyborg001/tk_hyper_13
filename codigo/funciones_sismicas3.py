#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 14:16:24 2018

@author: carlos
"""

import math
import threading
import os
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import eventsEndpoint as endpoint

""" construye un lista con los pares de coordenadas del poligono que forma la ciudad
    como argumento recibe a path, la direccion de la carpeta donde estan los archivos
    csv que contiene los puntos, y el nombre de la ciudad tal como esta en la carpeta
    los puntos pueden tener la dos sigts sintaxis ['-xxxxxxx,xxxxxxx'] o

    ['-xxxxxxxxx xxxxxxxxx']"""
def hacer_poligono(path,ciudad):

    path+='/'+ciudad
    archivo = open(path)
    s = archivo.readlines()
    l = []
    for n in s:
        if ',' in n:
            y = n.split(',')
            l.append([float(y[0]),float(y[1])])
        else:
            y = n.split()
            l.append([float(y[0]),float(y[1])])
    return l

#print(hacer_poligono('/home/carlos/Escritorio/tk_hyper_v7.3/provinciascsv','Region de Puerto Rico.csv'))


#funcion hacer_poligonos acepta una lista con los nombres de las carpetas
#donde estan las ubicaciones de cada provincia ['Azua.csv','Barahona.csv',...]
#devuelve una lista con las ciudades y sus respectivas listas de de ubicaciones
#que forma el poligono [['Azua',[[-xxxx, xxxxx],....],['Barahona',[-xxxx, xxxx],[],....]]
def hacer_poligonos(files,path_provincias):
    poligonos = []
    for n in files:
        # print(n)

        poligonos.append([n,hacer_poligono(path_provincias,n)])
    return poligonos

def esta(pd_arr,dimension,coordenada):
    if len(pd_arr[pd_arr[dimension]>= coordenada]) and \
        len(pd_arr[pd_arr[dimension]<= coordenada]):
            return True
    else:
        return False

def esta_en_poligono(path_poligono,lat,lon):
    pd_arr = pd.read_csv(path_poligono)
    pd_arr.columns = ['longitud','latitud']
    if esta(pd_arr,'longitud',lon) and esta(pd_arr,'latitud',lat):
        return True
    else:
        return False

# def punto_en_poligono(x, y, poligono):
#     #este codigo fue extraido de la pagina:https://sakseiw.wordpress.com
#     """Comprueba si un punto se encuentra dentro de un polígono
#
#        poligono - Lista de tuplas con los puntos que forman los vértices [(x1, x2), (x2, y2), ..., (xn, yn)]
#     """
#     i = 0
#     j = len(poligono) - 1
#     salida = False
#     for i in range(len(poligono)):
#         if (poligono[i][1] < y and poligono[j][1] >= y) or (poligono[j][1] < y and poligono[i][1] >= y):
#             if poligono[i][0] + (y - poligono[i][1]) / (poligono[j][1] - poligono[i][1]) * (poligono[j][0] - poligono[i][0]) < x:
#                 salida = not salida
#                 #print salida
#
#         j = i
#     return salida
#recibe la locacion del evento x,y y devuelve el nombre de la provincia donde esta el evento
#o False sino esta en ninguna de las provincias de la lista
def de_que_provincia_es(x,y,files,path_provincias):

    poligonos = hacer_poligonos(files,path_provincias)
    for n in poligonos:
        if punto_en_poligono(x,y,n[1])==True:

            return n[0][:-4]
    return False
#poligonos = hacer_poligonos(files)

# la funcion "haversine" recibe dos coordenadas(lat1,lon1) y (lat2 y lon2)
# devuelve la distancia ortodromica entre los puntos

def haversine(lat1,lon1,lat2,lon2):
  R = 6370
  dlat = lat2 - lat1
  dlon = lon2 - lon1
  D= 2*R*math.asin(math.sqrt(math.sin(math.radians(dlat/2))**2+
                             math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*
                     math.sin(math.radians(dlon/2))**2))

  return D
# la funcion calcular_ciudad calcula la ciudad importante mas cercana al sismo
# acepta 3 parametros el archivo con las ciudades y sus cordenadas, generado por
# la funcion formatear_lineas y la latitud y longitud del sismo sentido
def calcular_ciudad(ciudades,prov,lat,lon):

  l = [ciudades[prov]['ciudades'],ciudades[prov]['locacion']]
  dmin = 1000000
  ciudad = ''
  salida = []

  for i in range(len(l[1])):
    la = float(l[1][i][0])
    lo = float(l[1][i][1])
    d = haversine(lat,lon,la,lo)

    if d < dmin:
      dmin = d
      ciudad = l[0][i]
      salida = [la,lo,round(dmin,1),ciudad]
  return salida
# la funcion generar_comentario es la funcion que devuelve el comentario asociado
# con el sismo analizado con el siguiente formato: "3.0 Km al ONO de El Penon, Barahona."

def generar_comentario(ciudades,lat,lon,file_provincias):
  files = os.listdir(file_provincias)#tira el listado de las provincias(poligonos)
  prov_pol = de_que_provincia_es( lon,lat,files,file_provincias)#dice en que provincia esta el sismo,false si no esta en ningun poligono
  if prov_pol == False:
    return "Distante."
  v = calcular_ciudad(ciudades,prov_pol,lat,lon)#calcula la ciudad mas cercana dentro del poligono/provincia

  if v == False:
      return 'Fuera de la Region'
  direcciones = ['Este','ENE','NE','NNE','Norte','NNO','NO','ONO','Oeste','OSO','SO',
                 'SSO','Sur','SSE','SE','ESE']
  direccion =''
  cuadrante = 0
  dlat = lat -v[0]
  dlon = lon -v[1]
  if dlat > 0:
    if dlon >0:
      cuadrante = 1
    if dlon <0:
      cuadrante = 2
  else:
    if dlon > 0:
      cuadrante = 4
    if dlon < 0:
      cuadrante = 3
  c = 11.25 #grado de la rosa
  q = 22.5 #grados correspondientes a cada punto y subpuntos cardinales

  t = math.atan(dlat/dlon)

  t = math.degrees(t)

  if cuadrante == 2:
    t = 180 + t
  if cuadrante == 3:
    t = t + 180
  if cuadrante == 4:
    t = 360 +t
  #print t,cuadrante
  #condiciones para las direcciones
  if t < c:
    direccion = direcciones[0]
  if t >= c and t < c+q:
    direccion = direcciones[1]
  if t >= c+q and t < c+2*q:
    direccion = direcciones[2]
  if t >= c+2*q and t < c+3*q:
    direccion = direcciones[3]
  if t >= c+3*q and t < c+4*q:
    direccion = direcciones[4]
  if t >= c+4*q and t < c+5*q:
    direccion = direcciones[5]
  if t >= c+5*q and t < c+6*q:
    direccion = direcciones[6]
  if t >= c+6*q and t < c+7*q:
    direccion = direcciones[7]
  if t >= c+7*q and t < c+8*q:
    direccion = direcciones[8]
  if t >= c+8*q and t < c+9*q:
    direccion = direcciones[9]
  if t >= c+9*q and t < c+10*q:
    direccion = direcciones[10]
  if t >= c+10*q and t < c+11*q:
    direccion = direcciones[11]
  if t >= c+11*q and t < c+12*q:
    direccion = direcciones[12]
  if t >= c+12*q and t < c+13*q:
    direccion = direcciones[13]
  if t >= c+13*q and t < c+14*q:
    direccion = direcciones[14]
  if t >= c+14*q and t < c+15*q:
    direccion = direcciones[15]
  if t >= c+15*q and t < c+16*q:
    direccion = direcciones[0]
    #if n[0]== 'Elias Pina.csv':
             #   return 'Elias Piña'
            #if n[0]== 'Monsenor Nouel.cvs':
            #    return 'Monseñor Nouel'

  if prov_pol == 'Monsenor Nouel':
    prov_pol = 'Monseñor Nouel'
  if prov_pol ==  'Elias Pina':
    prov_pol ==  'Elias Piña'
  comentario = str(v[2])+" Km al " + direccion+ " de " + v[3]+', '+prov_pol+'.'
  return comentario

#prov = de_que_provincia_es(,get_lat(lat))
#prov = de_que_provincia_es( -71.529452,19.430041)

def get_ciudades(path_ciudades):

    archivo = open(path_ciudades)
    lista = archivo.readlines()
    l_final = []
    for e in lista:
        n = e.find('.')
        a =[e[:n].split(','),e[n+1:].split()]
        l_final.append(a)
    l_final.remove(l_final[0])
    ciudades = {}
    for e in l_final:
        ciudad = e[0][1][1:]
        #print ciudad
        if ciudad not in ciudades:
            ciudades[ciudad]={'ciudades':[e[0][0]],'locacion':[e[1]]}
        else:
            ciudades[ciudad]['ciudades'].append(e[0][0])
            ciudades[ciudad]['locacion'].append(e[1])
            #se genero un diccionario de ciudades con la sigt sintaxis:
            # ciudades['Valverde']={'ciudades':['Mao','Esperanza',...],'locacion':[['latitud','longitud'],...]}

    return ciudades





#comentario = generar_comentario(ciudades,  get_lat(lat), get_lon(lon), path_provincias)
#comentario = generar_comentario(ciudades, 19.3490, -68.4890, path_provincias)
def get_select(lineas,start,end):#devuelve un select de la lista lineas
                                #desde start hasta end
    return lineas[start:end]

def get_indices(lineas):#crea un arreglo con los indices iniciales de
                        #cada select
    indices = []
    i = 0
    while i < len(lineas):
        if lineas[i][-2]=='1':
            ind = lineas.index(lineas[i])
            indices.append(ind)
        i+=1
    indices.append(lineas.index(lineas[-2]))
    return indices


def formatear(select,ciudades,path_provincias):

    l1 = ''
    l2 = ''
    for n in select:
        if n[-2] == '1':
            l1 = n
        if n[-2] == 'E':
            l2 = n
    #crear fecha
    anio = l1[1:5]
    mes = l1[6:8]
    #aqui se le da formato de dos digitos al mes
    if mes[0]==' ':
        mes = '0'+mes[1]
    dia = l1[8:10]
    #aqui se completa el campo dia con dos digitos
    if dia[0]==' ':
        dia = '0'+dia[1]
    #aqui se completa la fecha
    fecha = anio+'-'+mes+'-'+dia

    #---------------------------------------------
    #aqui se formatea la hora
    h = l1[11:15]
    sec = l1[16:18]
    #se completan los segundos a dos digitios de ser necesario
    if sec[0]==' ':
        sec = '0'+sec[1]
    hora = h[:2]+':'+h[2:]+':'+sec

    #--------------------------------------------
    #las demas variables importantes de la primera linea
    lat = l1[24:30]
    lon = l1[31:38]
    prof = l1[38:43]
    gap = l2[5:8]
    eprof = l2[38:43]
    rms = l1[52:55]
    #----------------------------------------------------
    #aqui se seleccionan las magnitudes
    l = l1[56:].split()
    ml ='---'
    mc ='---'
    mw ='---'
    for n in l:
        if 'L' in n:
            ml = n[:3]
        if 'C' in n:
            mc = n[:3]
        if 'W' in n:
            mw = n[:3]
    salida = fecha +' '+hora+' '+lat+' '+lon+' '+prof+ \
    '  '+eprof+'  '+gap+'  '+rms+'  '+ml+'  '+mc+'  '+mw+ ' '
    comentario = generar_comentario(ciudades,float(lat),float(lon),path_provincias)
    return salida + comentario
#--------------------------------------------------------
def crear_header():#crea la cabecera o titulo de la base de datos
    return 'fecha      hora     lat    lon      dep    edep  gap  rms  ml   mc   mw  comentario\n'

#-----------------------------------------------------------------
def anadir_registro(lineas,ciudades,select,path_provincias,out):#abre el archivo para anadir un nuevo registro
    salida = open(out,'a')
    salida.write(formatear(select,ciudades,path_provincias)+'\n')
    salida.close()

#------------------------------------------------------------------
def crear_dbd(lineas,ciudades,path_provincias,out):#crea la base de datos
#ciudades es un diccionario con
    salida = open(out,'w')
    header = crear_header()
    salida.write(header)
    salida.close()
    v = get_indices(lineas)

    #bucle para extraer los datos y anadirlos a la base de datos
    i = 0
    while i+1 < len(v):
        select = get_select(lineas,v[i],v[i+1])
        anadir_registro(lineas,ciudades,select,path_provincias,out)
        i+=1
def ordenar(arr):
    for i in range(len(arr)-1):
        for j in range(len(arr)-1):
            if arr[j].split()[0] > arr[j+1].split()[0]:
                temp = arr[j]
                arr[j] = arr[j+1]
                arr[j+1]=temp
    return arr

#'jleonel78@uasd.edu.do','amoreta78@uasd.edu.do'


def enviarEmail(destinatario,msg,sentido,paths,modo='html'):#el modo indica si el correo es texto o html
    #por default el modo es 'plain', sino se puede cambiar a 'html'
    print('enviando mail...')
    sentido_local = sentido
    usuario = paths[4][:-1]
    clave = paths[5][:-1]
    # print(usuario,clave)

    str_sentido=''
    if sentido==True:
        str_sentido = ' <strong>(Sentido).<strong>'
    else:
        str_sentido=''
    def calcular_hora(hora):
        h=hora.split(':')
        #print(h)
        if int(h[0])<4:
            return str(int(h[0])+20)+':'+h[1]+':'+h[2]
        else:
            s = str(int(h[0])-4)+':'+h[1]+':'+h[2]
            if len(s)<8:
                s= '0'+s
            return s

    '''
    esta funcion recibe un arreglo de correos electronicos, y un mensaje diccionario
    python el cual contiene el siguiente formato:
    obj ={'comentario': '13.4 Km al Este de Mano Juan Isla Saona, Isla Saona.',
         'depth': '120.1',
         'fecha': '2014-07-02',
         'hora': '28:02:31',
         'lat': '18.129',
         'lon': '-68.604',
         'mag': '3.9'}


    destinatario =['cramirez27@uasd.edu.do','cgrs27@gmail.com',
    'jleonel78@uasd.edu.do','amoreta78@uasd.edu.do']
    '''
    asunto ="Evento analizado el "+ msg["fecha"]+ " a las "+ msg["hora"]
    if 'Km' not in msg["depth"]:
        msg["depth"]+='Km'
    msg1 = msg.copy()
    msg["comentario"]=msg["comentario"].replace(',','.')+str_sentido
    user = usuario
    password = clave
    #print(msg['comentario'])
    remitente = 'CNS <analisisuasd2015@gmail.com>'

    st=''
    orden = ['fecha','hora','lat','lon','depth','mag','comentario']
    for i in orden:
        if i == 'hora':
            st+='Hora UTC: %s<br>Hora Local: %s<br>'%(str(msg[i]),calcular_hora(str(msg[i])))
        else:
            st+=str(i).capitalize()+': '+str(msg[i]) +'<br>'
    # print(st)

    mensaje= """\
    <html>
        <head></head>
        <body style='background:#F0F7D4'>
            <div style='background:#B2D732; text-align:center;padding:15px'>
                <h3 style='color:black'><strong>REPORTE DE SISMO</strong></h3>
            </div>
            <div style="color:black;padding:10px 3px">
            """+st+"""
            </div>
        </body>
        <footer style='background-color:#092834;text-align:center;
                                        color:#66B032; padding:10px 5px'>
                                        CNS</footer>

    </html>
    """
    msg = msg1.copy()
    orden1 = ''
    datos = ''
    for n in orden:
        orden1+=n+', '
        datos+=msg1[n]+', '
    adjunto = '''%s
%s'''%(orden1[:-2],datos[:-2])

    gmail = smtplib.SMTP('smtp.gmail.com',587)

    gmail.starttls()
    gmail.login(user,password)
    #gmail.set_debuglevel(1)

    header = MIMEMultipart()
    header['Subject']=asunto
    header["From"]=remitente
    header["To"]= destinatario[0]

    reporte = MIMEText(mensaje,modo)#si quieres en texto plano cambiar html por plain

    header.attach(reporte)
    adjunto_MIME = MIMEBase('multipart','plain')
    adjunto_MIME.set_payload(adjunto)
    encoders.encode_base64(adjunto_MIME)
    adjunto_MIME.add_header('Content-Disposition',"attachment;filename= %s" %'reporte.csv')
    header.attach(adjunto_MIME)
    #enviar email
    gmail.sendmail(remitente,destinatario,header.as_string())
    #cerrar la coneccion SMTP
    gmail.quit()
    print("mail enviado!")
#formatear_hyp()es una funcion que extrae los datos del archivo dummyx.dat
def formatear_hyp(linea,path_poligonos,path_ciudades,magni=1):
    anio = linea[1:5]
    mes = linea[6:8]
    dia = linea[8:10]
    if mes[0]==' ':
        mes=str(0)+mes[1]
    if dia[0]== ' ':
        dia = str(0)+dia[1]
    h = linea[11:13]
    if h[0]==' ':
        h =  str(0)+h[1]
    m = linea[13:15]
    if m[0]==' ':
        m = str(0)+m[1]
    s = linea[16:18]
    if s[0]==' ':
        s = str(0)+s[1]
    lat = linea[24:30]
    lon = linea[31:38]
    fecha = anio+'-'+mes+'-'+dia
    hora = h+':'+m+':'+s
    i_d = anio+mes+dia+h+m
    deph = linea[38:43]
    l = linea[56:-1]
    ml = '0.0'
    mc = '0.0'
    mw = '0.0'
    mag = '0.0'
    if 'L' in l:
        ml = l[l.index('L')-3:l.index('L')]
    if 'C' in l:
        mc = l[l.index('C')-3:l.index('C')]
    if 'W' in l:
        mw = l[l.index('W')-3:l.index('W')]
    if mc!='':
        mag = mc
    elif ml !='':
        mag = m
    else:
        mag = mw
    if magni==1:
        mag=mc
    if magni==2:
        mag=ml
    if magni==3:
        mag=mw
    if magni==4:
        prom = promedio(float(ml),float(mc),float(mw))
        if prom != 0:
            mag = str(prom)
        else:
            mag = "0.0"




    sal=i_d+ '  '+fecha+'  '+hora+'  '+lat+'  '+lon+'  '+deph+'  '+mag+'  '
    comentario = generar_comentario(path_ciudades,float(lat),float(lon),path_poligonos)
    #json = "{'i_d':'"+i_d+"','fecha':'"+fecha+"','hora':'"+hora+"','lat':'"+lat+"','lon':'"+lon+"','deph':'"+deph+"','mag':'"+mag+"','comentario':'"+comentario+"}"
    obj = {'id':i_d,"fecha":fecha, "hora":hora, "lat":lat, "lon":lon, "depth":deph, "mag":mag, "comentario":comentario,"salida":sal,"tipo_magni":magni}
    #print (json.dumps(obj))
    # return sal + comentario,i_d,sal,obj,comentario
    return obj

def formatear_dummy(linea,ciudades,path_provincias):
    linea = linea.split()
    lat = linea[1]
    lon = linea[2]
    deph = str(float(linea[3]))
    dif = 5-len(deph)
    if dif != 0:
        deph = dif*' '+deph
    dia = linea[6]
    if len(dia)==1:
        dia = '0'+dia
    mes = linea[7]
    if len(mes)==1:
        mes = '0'+mes
    anno = linea[8]
    fecha = anno+'-'+mes+'-'+dia
    h= linea[9]
    dif = 2-len(h)
    if dif != 0:
        h = dif*'0'+h
    m = linea[10]
    dif = 2-len(m)
    if dif != 0:
        m = dif*'0'+m
    s = linea[11]
    dif = 2-len(s)
    if dif != 0:
        s = dif*'0'+s
    hora = h+':'+m+':'+s
    mag = linea[21]
    i_d = anno+mes+dia+h+m
    salida  = i_d+'  '+fecha+'  '+hora+'  '+lat+'  '+lon+'  '+deph+'  '+mag
    comment = generar_comentario(ciudades,float(lat),float(lon),path_provincias)
    comentario = salida +'  '+comment
    obj = {"fecha":fecha, "hora":hora, "lat":lat, "lon":lon, "depth":deph,
           "mag":mag, "comentario":comment}
    return comentario,i_d,salida,obj

def promedio(ml,mc,mw):
    numeros = [float(ml),float(mc),float(mw)]
    prom = 0
    n = 0
    for i in range(len(numeros)):
        if numeros[i] != None and numeros[i] != 0:
            prom+=numeros[i]
            n+=1
        #print(f'{promedio} {n}')
    prom/=n
    return float(round(prom,1))


def insertar_comentario(paths,formato,sentido):
    '''esta funcion acepta la ruta de un archivo y si el archvio tiene el formato indicado
    anade o reescribe la linea del comentario en (LOCALITY:)  por el segundo argumento (comentario) '''
    #paths = open(paths).readlines()
    print("Insertando comentario....")
    if sentido == True:
        sentido_local = '(Sentido).'
    else:
        sentido_local = ''
    #print(formato["tipo_magni"])
    base = paths[6][:-1]
    ruta_hyp = paths[0][:-1]
    lineas_hyp = open(ruta_hyp).readlines()
    region = lineas_hyp[0][21]
    id= ''
    for linea in lineas_hyp:
        if "ID:" in linea:
            pos_id = linea.index("ID:")+3
            id = linea[pos_id:pos_id+14]
    anio = id[:4]
    mes = id[4:6]
    # 2019 02 04143300
    dia = id[6:8]
    hhmm = id[8:12]
    ss = id[12:14]
    base = base + "\\%s\\%s" % (anio,mes)
    nombre = "%s-%s-%s%s.S%s%s" % (dia,hhmm,ss,region,anio,mes)
    ruta_nombre = os.path.join(base,nombre)
    if ruta_nombre == None or os.path.isdir(ruta_nombre):
        return None
    comentario = formato["comentario"]+sentido_local
    archivo = open(ruta_nombre,'r')
    lineas = archivo.readlines()
    archivo.close()

    ini = " LOCALITY: "
    blanco = 81-2-len(ini)-len(comentario)
    comment = ini+comentario+' '*blanco+'3\n'
    # z=  ' LOCALITY: 44.0 Km al SO de Ponce, Region de Puerto Rico.                      3\n'
    hay_comment = False
    temp =None
    for n in lineas:
        if 'LOCALITY:' in n:
            # lineas[lineas.index(n)] = comment
            temp = n
            hay_comment = True
            break
    if hay_comment == False:
        lineas.insert(1,comment)
    else:
        lineas[lineas.index(temp)] = comment
    archivo = open(ruta_nombre,'w')
    archivo.writelines(lineas)
    # print(archivo.read())
    archivo.close()
    thread = threading.Thread(target=EnviarEventoABD, args=(nombre,sentido,formato["tipo_magni"]))
    thread.start()


def EnviarEventoABD(nombre,sentido,tipoMagnitud):
    enviarReq = endpoint.EventsEndpoint()
    reqResult=enviarReq.EnviarEvento(nombre,sentido,tipoMagnitud)
    return reqResult

def guardar_datos(paths,formato,sentido):
        print("Guardando los datos en dummyX.dat,dummyX.copy.....")
        salida = paths[1][:-1]#'dummyX.dat'#r'X:\dummyX.dat'
        fsalida = open(salida,'w')

        if sentido == True:
            sentido_local = ' (Sentido)'
        else:
            sentido_local =''
        datos = formato['salida']+formato['comentario']+sentido_local
        with open(salida,'w') as fsalida:
            fsalida.write(datos)
        fsalida.close

        salida_copy =  paths[2][:-1]#'dummyX.copy'#r'Z:\seismo\WOR\dummyX.copy'
        if os.path.isfile(salida_copy)==False:
            fsalida = open(salida_copy,'w')
            fsalida.close()

        with open(salida_copy,'r') as fsalida:
            s_salida = fsalida.readlines()
        fsalida.close()
        i_d=[]
        for n in s_salida:
            if len(n)<10:
                s_salida.remove(n);
        for n in s_salida:
            i_d.append(n.split()[0])
        if formato['id'] not in i_d:
            s_salida.append(datos+'\n')
        else:
            s_salida[i_d.index(formato['id'])] = datos+'\n'
        s_salida = ordenar(s_salida)
        salida =""

        for n in s_salida:
            salida+=n

        with open(salida_copy,'w') as fsalida:
            fsalida.write(salida)
        fsalida.close()
        print("Datos guardados!")
        #aqui se crea la base da datos json
        #si el archivo esta vacion se crea la lista de jsons
        # path_json = paths[3][:-1]
        # if os.path.isfile(path_json)==False or open(path_json,'r').read()==''or open(path_json,'r').read() == None:
        #     fjson = open(path_json,'w')
        #     json.dump(formato,fjson)
        #     fjson.close()
        # else:
        #     fjson = open(path_json,'r')
        #     mijson = json.load(fjson)
        #     fjson.close()
        #     print(mijson)
        #     if formato not in mijson:
        #         mijson.append(formato)
        #         fjson = open(path_json,'w')
        #         json.dump(mijson,fjson)
        #     fjson.close()
# paths="paths.txt"
# insertar_comentario(paths,"formato")
#
# path = os.getcwd()
# ruta = ultimo_archivo(path)
# comentario='44.0 Km al SO de Ponce, Rico.'
# insertar_comentario(ruta,comentario)
