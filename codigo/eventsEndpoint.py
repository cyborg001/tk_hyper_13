import codigo.httpRequests as req
import json
import os

class EventsEndpoint:
    serverData={}
    def __init__(self):
        with (open(os.path.join('utiles','config.json'))) as json_file:
            self.serverData=json.load(json_file)
        super().__init__()

    def SendEvent(self,event,felt,selectedMag,token, magObj):
        toSend= EventFromFile(event,felt,selectedMag,magObj)
        conn = req.HttpRequest(self.serverData['endpointUrl'])
        return conn.MakeRequest("/api/Events/UpdateEventFromFileNew",req.HttpMethods.PUT,toSend,"",{
            "content-type":"application/json",
            "Authorization":"bearer "+token
        })

    def AddBulleting(self,startDate,endDate,feltEvents,token):
        toSend= AddBulletingClass(startDate,endDate,feltEvents)
        conn = req.HttpRequest(self.serverData['endpointUrl'])
        return conn.MakeRequest("/api/Boletin/CrearBoletin",req.HttpMethods.POST,toSend,"",{
            "content-type":"application/json",
            "Authorization":"bearer "+token
        })

    def SendBulleting(self,startDate,endDate,feltEvents,token):
        toSend= AddBulletingClass(startDate,endDate,feltEvents)
        conn = req.HttpRequest(self.serverData['endpointUrl'])
        return conn.MakeRequest("/api/Boletin/EnviarBoletin",req.HttpMethods.POST,toSend,"",{
            "content-type":"application/json",
            "Authorization":"bearer "+token
        })


    def Login(self,username='',password=''):
        toSend =  LoginClass(self.serverData['username'],self.serverData['password'])
        conn = req.HttpRequest(self.serverData['endpointUrl'])
        return conn.MakeRequest("/api/Login",req.HttpMethods.POST,toSend,"",{
            "content-type":"application/json"
        })
# METODO PARA ENVIAR EL EVENTO A LA BASE DE DATOS. PARAMETROS: -Evento: nombre archivo Seisan, -Sentido: indica si el evento fue sentido
    def EnviarEvento(self,evento,sentido=False,magnitudSeleccionada='', magObj={}):
        token = self.Login()
        if token['status']>=0:
            return self.SendEvent(evento,sentido,magnitudSeleccionada,token['token'],magObj)
        else:
            return {'status':-1}
# METODO PARA CREAR EL BOLETIN. PARAMETROS: -Fecha inicio: fecha desde (vacio hace el del dia de hoy desde las 00:00:00 a la hora actual), -Fecha Final: fecha Hasta (vacio hace el del dia de hoy)
# -Eventos sentidos: indica si solo hace reporte de los eventos sentidos solamente
    def CrearBoletin(self,fechaInicio,fechaFin,eventosSentidos=False):
        token = self.Login()
        if token['status']>=0:
            return self.AddBulleting(fechaInicio,fechaFin,eventosSentidos,token['token'])
        else:
            return {'status':-1}
# METODO PARA CREAR Y ENVIAR EL BOLETIN. PARAMETROS: -Fecha inicio: fecha desde (vacio hace el del dia de hoy desde las 00:00:00 a la hora actual), -Fecha Final: fecha Hasta (vacio hace el del dia de hoy)
# -Eventos sentidos: indica si solo hace reporte de los eventos sentidos solamente
    def EnviarBoletin(self,fechaInicio,fechaFin,eventosSentidos=False):
        token = self.Login()
        if token['status']>=0:
            return self.SendBulleting(fechaInicio,fechaFin,eventosSentidos,token['token'])
        else:
            return {'status':-1}



    def ValidateUser(self,token):
        conn = req.HttpRequest(self.serverData['endpointUrl'])
        return conn.MakeRequest("/api/Login/Validate",req.HttpMethods.GET,"","",{
            "content-type":"application/json",
            "Authorization":"bearer "+token
        })


class LoginClass:
    def __init__(self,user,passwrd):
            self.username=user
            self.password=passwrd
            super().__init__()
    username=''
    password=''
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

class AddBulletingClass:
    def __init__(self,startDate,endDate,feltEvent):
            self.startDate=startDate
            self.endDate=endDate
            self.feltEvent=feltEvent
            super().__init__()
    startDate=''
    endDate=''
    feltEvent=False
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)


class EventFromFile:
    def __init__(self,fileName,felt,selectedMag,dataObj):
            self.fileName=fileName
            self.felt=felt
            self.fileData=dataObj
            self.selectedMagnitude=selectedMag
            super().__init__()
            
    fileName=''
    fileData={}
    felt=False
    selectedMagnitude=''
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

class EventObj:
    def __init__(self,lat,lon,depth,fecha,hora,rms,mag,magC,magL,magW,comentario,salida,tipo_magni,gapInfo=[],focalInfo=[]):
        self.lat=float(lat)
        self.lon=float(lon)
        self.depth=float(depth)
        self.rms=float(rms)
        self.mag=float(mag)
        self.magC=float(magC)
        self.magL=float(magL)
        self.magW=float(magW)
        self.tipo_magni=tipo_magni
        self.gapInfo=gapInfo
        self.focalInfo=focalInfo
        self.fecha=fecha
        self.hora=hora
        self.comentario=comentario
        self.salida=salida

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

