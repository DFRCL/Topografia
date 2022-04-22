# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import csv
import sys
from dxfwrite import DXFEngine as dxf
from tkFileDialog   import askopenfilename
from tkFileDialog import asksaveasfilename
from angles import deci2sexa

tolerancia_hilos = 0.001 #Error permitido en la comprobacion de hilos
tolerancia_area = 0.001 #Error Unitario Area
tolerancia_error_unitario = 0.003 #Valor de error unitario permisible
tolerancia_angular = 0 #Configurar al desarrollar métodos
constante_taquimetria = 100 #Constante reducción del instrumento optico usado

class Punto(object):
    all = []

    def __init__(self, Nombre, X, Y, Z, origen=False):
        self.Nombre=Nombre
        self.X=X
        self.Y=Y
        self.Z=Z
        self.origen = origen
        Punto.all.append(self)
       
    def __str__(self):
	clase = type(self).__name__
	msg = "{0} {1}({2},{3},{4})"
	return msg.format(clase, self.Nombre, self.X, self.Y, self.Z)
	
class Vector(object):
    all = []
    
    def __init__(self, EST, PO, x, y, z):
        self.EST = EST
        self.PO = PO
        self.x = x
        self.y = y
        self.z = z
        Vector.all.append(self)
        
    def __str__(self):
	clase = type(self).__name__
	msg = "{0} (EST:{1} PO:{2} x:{3} y:{4}, z: {5})"
	return msg.format(clase, self.EST, self.PO, self.x, self.y, self.z)
        
class Levantamiento(object):
    current = 0
    all = []
    
    def __init__(self, Nombre, Responsables, Ubicacion, Fecha , Hora, Instrumento, Metodos):
        Levantamiento.current = self
        self.Nombre  =  Nombre
        self.Responsables  =  Responsables
        self.Ubicacion = Ubicacion
        self.Fecha = Fecha
        self.Hora = Hora
        self.Instrumento = Instrumento
        self.Metodos = Metodos
        self.Tolerancia_Area = tolerancia_area 
        self.Tolerancia_Error_Unitario = tolerancia_error_unitario
        Levantamiento.all.append(self)
        self.Observaciones = []
        
    def levantamiento_actual(self):
        Levantamiento.current = self
    
    def __str__(self):
	clase = type(self).__name__
	msg = "{0}: {1} \n Responsables: {2}\n Ubicacion:{3}\n Fecha y Hora:{4}, {5}\n Instrumento: {6}\n Metodo(s): {7}"
	return msg.format(clase, self.Nombre, self.Responsables, self.Ubicacion, self.Fecha, self.Hora, self.Instrumento, self.Metodos)
        
class Observacion(object):
    all = []

    def __init__(self, Metodo, Datos):
        self.Metodo = Metodo
        self.Datos = Datos
        Levantamiento.current.Observaciones.append(self)
        Observacion.all.append(self)
        self.ID = Observacion.all.index(self)
     
    def __str__(self):
	clase  =  type(self).__name__
	msg  =  "{0}, Metodo: {2}, ID: {1}"
	return msg.format(clase, self.ID ,self.Metodo)

class Radiacion(Observacion):
    all = []
    
    def Parciales(self):
        y = self.Distancia*np.cos(np.radians(self.Azimut))
        x = self.Distancia*np.sin(np.radians(self.Azimut))
        return x,y

    def __init__(self, **kwargs):
        Observacion.__init__(self, 'Radiacion', kwargs)
        self.PO = kwargs.get('PO')
        self.EST = kwargs.get('EST')
        self.Descripcion = kwargs.get('Descripcion')
        self.Poligono = kwargs.get('Poligono')
        self.Azimut = kwargs.get('Grados')+(kwargs.get('Minutos')/60.0)+(kwargs.get('Segundos')/3600.0)
        self.Distancia = kwargs.get('Distancia') #Distancia Horizontal
        self.Parciales = self.Parciales()
        self.x = self.Parciales[0]
        self.y = self.Parciales[1]
        self.z = 0
        Radiacion.all.append(self)
        
    def __str__(self):
	clase  =  type(self).__name__
	msg  =  "{0} (PO: {1} DH: {2} Az: {3})"
	return msg.format(clase, self.PO, self.Distancia, self.Azimut)      

class Cilindricas(Radiacion):
    all =[]
    #Notar que la Distancia representa el radio y no la Distancia Horizontal
    def __init__(self, **kwargs):
        Radiacion.__init__(self, **kwargs)
        self.z = kwargs.get('Desnivel')
        Cilindricas.all.append(self)
        
class Esfericas(Observacion):
     #Notar que la Distancia representa el radio y no la Distancia Horizontal
    def Parciales(self):
        y = self.Distancia*np.cos(np.radians(self.Azimut))*np.sin(np.radians(self.Zenital))
        x = self.Distancia*np.sin(np.radians(self.Azimut))*np.sin(np.radians(self.Zenital))
        z = self.Distancia*np.cos(np.radians(self.Zenital))
        return x,y,z 
     
    def __init__(self, **kwargs):
        Observacion.__init__(self, 'Radiacion Esferica', kwargs)
        self.EST = kwargs.get('EST')
        self.PO = kwargs.get('PO')
        self.Descripcion = kwargs.get('Descripcion')
        self.Poligono = kwargs.get('Poligono')
        self.Azimut = kwargs.get('Grados')+(kwargs.get('Minutos')/60.0)+(kwargs.get('Segundos')/3600.0)
        self.Distancia = kwargs.get('Distancia')
        self.Zenital = kwargs.get('Zenital')
        self.Parciales = self.Parciales()
        self.x = self.Parciales[0]
        self.y = self.Parciales[1]
        self.z = self.Parciales[2]
        Esfericas.all.append(self)
    
    def __str__(self):
	clase  =  type(self).__name__
	msg  =  "{0} (PO: {1} DH: {2} Az: {3} Zenital: {4})"
	return msg.format(clase, self.PO, self.Distancia, self.Azimut, self.Zenital)

class Taquimetria(Observacion):
    all = []
    
    def comprobacion_hilos(self):
        if (self.HS+self.HI)/2-tolerancia_hilos <= self.HM >= (self.HS+self.HI)/2+tolerancia_hilos:
            return True
        else:
            print 'Por Favor Verificar las lecturas de Hilos en Punto %s' %self.Nombre
            
    def distancia_horizontal(self):
        if self.comprobacion_hilos() == True:
            self.DH = (constante_taquimetria*(self.HS-self.HI)*(np.sin(np.radians(self.Zenital)))**2)
        else:
            self.DH = 0
        return self.DH
            
    def distancia_vertical(self):
        if self.comprobacion_hilos() == True:
            self.DV = (0.5*constante_taquimetria*(self.HS-self.HI)*(np.sin(np.radians(2*self.Zenital))))
        else:
            self.DV = 0
        return self.DV
            
    def Parciales(self):
        self.distancia_horizontal()
        self.distancia_vertical()
        x = self.DH * np.sin(np.radians(self.Azimut))
        y = self.DH * np.cos(np.radians(self.Azimut))
        return x, y
    
    def __init__(self, **kwargs):
        Observacion.__init__(self, 'Taquimetria', kwargs)
        self.EST = kwargs.get('EST')
        self.PO = kwargs.get('PO')
        self.Descripcion = kwargs.get('Descripcion')
        self.Poligono = kwargs.get('Poligono')
        self.Azimut = kwargs.get('Azimut')
        self.HS = kwargs.get('HS')
        self.HM = kwargs.get('HM')
        self.HI = kwargs.get('HI')
        self.Zenital = kwargs.get('GradosZ')+(kwargs.get('MinutosZ')/60.0)+(kwargs.get('SegundosZ')/3600.0)
        self.x = self.Parciales()[0]
        self.y = self.Parciales()[1]
        self.z = 0
        self.DH = self.distancia_horizontal()
        self.DV = self.distancia_vertical()
        Taquimetria.all.append(self)
       
    def __str__(self):
	clase  =  type(self).__name__
	msg  =  "{0}(PO: {1} DH:{2} AZ: {3})"
	return msg.format(clase, self.PO, self.DH, self.Azimut)
	
class Taquimetria3D(Taquimetria):
    all = []
    
    def Desnivel(self):
        self.distancia_vertical()
        desnivel = self.hi + self.DV - self.HM
        return desnivel
    
    def __init__(self, **kwargs):
        Taquimetria.__init__(self, **kwargs)
        self.hi = kwargs.get('hi')
        self.z = self.Desnivel()
        Taquimetria3D.all.append(self)
        
    def __str__(self):
	clase  =  type(self).__name__
	msg  =  "{0}(PO: {1} DH:{2} AZ: {3} hi: {4})"
	return msg.format(clase, self.PO, self.DH, self.Azimut, self.hi)
	
class Cartesiana_relativa(Observacion):
    all = []
    
    def __init__(self, **kwargs):
        Observacion.__init__(self, 'Cartesiana Relativa', kwargs)
        self.EST = kwargs.get('EST')
        self.PO = kwargs.get('PO')
        self.Descripcion = kwargs.get('Descripcion')
        self.x = kwargs.get('x')
        self.y = kwargs.get('y')
        self.z = kwargs.get('z')
        Cartesiana_relativa.all.append(self)
        
    def __str__(self):
	clase = type(self).__name__
	msg = "{0} {1}(Delta x= {2},Delta y= {3},Delta z= {4})"
	return msg.format(clase, self.PO, self.x, self.y, self.z)
	
class Deflexion(Observacion):
    all = []
    
    def Parciales(self):
        x = self.Distancia * np.sin(np.radians(self.Direccion_Linea_Resultante))
        y = self.Distancia * np.cos(np.radians(self.Direccion_Linea_Resultante))
    #Sentido +1 o -1 
    def __init__(self,**kwargs):
        Observacion.__init__(self, 'Deflexion', kwargs)
        #self.Direccion_Linea_Ref = Direccion_Linea_Ref
        self.EST = kwargs.get('EST')
        self.Deflexion = kwargs.get('GradosDef')+(kwargs.get('MinutosDef')/60.0)+(kwargs.get('SegundosDef')/3600.0)
        self.Sentido = kwargs.get('Sentido')
        self.Direccion_Linea_Resultante = self.Direccion_Linea_Ref + (self.Deflexion*self.Sentido)
        self.x = Parciales()[0]
        self.y = Parciales()[1]
        Deflexion.all.append(self)

def buscador_objetos_general(Nombre_objeto, clase):
    for p in clase.all:
        if p.PO==Nombre_objeto:
            return p      

def contra_azimut(azimut):
    CAZ = 0
    if azimut >= 180:
        CAZ = azimut-180
    else:
        CAZ = azimut+180

class Poligono(object):
    all = []

    def __init__(self, Nombre, Descripcion):
        self.Nombre = Nombre
        self.Puntos = []
        self.Descripcion = Poligono
        Poligono.all.append(self)

    def add_points(self):
        puntos = []
        for i in Observacion.all:
            if i.Poligono.lower() == self.Nombre.lower():
                puntos.append(i)
        self.Puntos = puntos
        
    def __str__(self):
	clase = type(self).__name__
	msg = "{0} {1}"
	return msg.format(clase, self.Nombre)
	
def Sumatoria(lista):
    suma=0
    for i in lista:
        suma += i
    return suma

def Total(lista):
    suma=0
    for i in lista:
        suma += abs(i)
    return suma	

	
class PoligonoCerrado(Poligono):
    all = []
    
    #errorunitario=np.sqrt(sumatoria(x_aux)**2+sumatoria(y_aux)**2)/sumatoria(DH_aux)
    
    def __init__(self, Nombre, Descripcion):
        Poligono.__init__(self, Nombre, Descripcion)
        self.Area=0
        self.Perimetro=0
        PoligonoCerrado.all.append(self)
    
class PoligonoAbierto(Poligono):
    all = []
    
    def __init__(self, Nombre, Descripcion):
        Poligono.__init__(self, Nombre, Descripcion)
        self.Longitud=0
        PoligonoAbierto.all.append(self)

class PoligonoAuxiliar(Poligono):
    all = []
    
    def error_unitario(self):
        pass
    
    def compensadas(self):
        def fc(eje):
            lista = []
            for punto in self.Puntos:
                lista.append(getattr(punto,str(eje)))
            if Sumatoria(lista) == 0:
                return 0
            else:
                return abs(Sumatoria(lista)/Total(lista))
            
        def signo(eje):
            lista = []
            for punto in self.Puntos:
                lista.append(getattr(punto,str(eje)))
            if Sumatoria(lista)<0:
                return 1
            elif Sumatoria(lista)==0:
                return 0
            else:
                return -1
            
        def compensar_eje(punto, eje):
            s = signo(eje)
            fc_eje = fc(eje)
            return getattr(punto, eje)+(s*abs(getattr(punto, eje)*fc_eje))

        def compensar(punto):
            return compensar_eje(punto, 'x'), compensar_eje(punto, 'y'), compensar_eje(punto, 'z')

        for i in self.Puntos:
            i.x = compensar(i)[0]
            i.y = compensar(i)[1]
            i.z = compensar(i)[2]
            
    def add_points(self):
        puntos = []
        for i in Observacion.all:
            if i.Poligono.lower() == self.Nombre.lower():
                puntos.append(i)
        self.Puntos = puntos

    def __init__(self, Nombre, Descripcion):
        self.Nombre = Nombre
        self.Descripcion = Descripcion
        Poligono.__init__(self, Nombre, Descripcion)
        PoligonoAuxiliar.all.append(self)
        #self.Estaciones = 0
        
class CurvaCircular(object):
    all = []

    def __init__(self, **kwargs):
        self.Nombre = kwargs.get('Nombre')
        self.CentroX = kwargs.get('CentroX')
        self.CentroY = kwargs.get('CentroY')
        self.Radio = kwargs.get('Radio')
        self.Delta = kwargs.get('Delta')
        self.LC = 0
        self.CM = 0
        CurvaCircular.all.append(self)
    
    def __str__(self):
	clase = type(self).__name__
	msg = "{0} {1} R: {2} Delta: {3}"
	return msg.format(clase, self.Nombre, self.Radio, self.Delta)

def Nuevo_levantamiento():
    Nombre = raw_input('Ingrese el nombre del levantamiento: ')
    Responsables = raw_input('Responsables del levantamiento: ')
    Ubicacion = raw_input('Ubicacion: ')
    Fecha = raw_input('Fecha del levantamiento: ')
    Hora = raw_input('Hora del levantamiento: ')
    Instrumento = raw_input('Instrumento: ')
    Metodos = raw_input('Metodo(s) Utilizado(s): ')
    
    Levantamiento(Nombre, Responsables, Ubicacion, Fecha, Hora, Instrumento, Metodos)
    
def estacion_inicio():
    Nombre = raw_input('Ingrese el nombre de la estacion de inicio: ')#+'(Estacion Inicial)'
    X = input('Ingrese X: ')
    Y = input('Ingrese Y: ')
    Z = input('Ingrese Z: ')
    Punto_inicio = Punto(Nombre, X, Y, Z, origen=True)

def buscador_objetos(Nombre_estacion):
    for p in Punto.all:
        if p.Nombre==Nombre_estacion:
            return p

def Correspondencia_PO_EST(Objeto_punto):
    return Objeto_punto.EST

def Vinculacion_PO_EST(o):
    return buscador_objetos(Correspondencia_PO_EST(o))

def build_vector(Observacion):
    return Vector(Vinculacion_PO_EST(Observacion), Observacion.PO, Observacion.x, Observacion.y, Observacion.z)

def Calculo_Totales(Vector):
    
    X = 0
    Y = 0
    Z = 0
    
    X = Vector.EST.X + Vector.x
    Y = Vector.EST.Y + Vector.y
    Z = Vector.EST.Z + Vector.z
    
    return Punto(Vector.PO , X, Y, Z)

def Totales(observacion):
    Calculo_Totales(build_vector(observacion))

def Plot():
    
    fig = plt.figure()
    ax3 = fig.add_subplot(1, 1, 1,aspect='equal')

    axes = plt.gca()
    # recompute the ax.dataLim
    ax3.relim()
    # update ax.viewLim using the new dataLim
    ax3.autoscale_view()
    
    for p in Punto.all:
        ax3.scatter(p.X, p.Y)
    
    for p in Punto.all:
        ax3.annotate(p.Nombre, (p.X,p.Y))
        
    plt.show()
    fig.savefig("Dibujo.pdf",format="pdf")

data_types = {'X':float, 
    'Y':float, 
    'Z':float, 
    'Nombre': float, 
    'Responsables': float,
    'Ubicacion': float,
    'Fecha': str,#REVISAR IMPLEMENTACION
    'Hora' : str,#REVISAR IMPLEMENTACION
    'Instrumento' : str,
    'Metodos' : str,
    'EST' : str,
    'PO' : str,
    'Descripcion': str,
    'Poligono' : str,
    'Azimut': float,
    'Grados' : int,
    'Minutos' : int,
    'Segundos' : float,
    'Distancia' : float,
    'GradosZ' : int,
    'MinutosZ' : int,
    'SegundosZ' : float,
    'Zenital' : float,
    'Desnivel' : float,
    'HS' : float,
    'HM' : float,
    'HI' : float,
    'hi' : float,
    'x' : float,
    'y' : float,
    'z' : float,
    'Deflexion' : float,
    'GradosDef' : float,
    'MinutosDef' : float,
    'SegundosDef' : float,
    'Sentido' : int,
    'CentroX' : float,
    'CentroY' : float,
    'CentroZ' : float,
    'Radio' : float,
    'Delta' : float,
    'Observaciones' : str,
    'Vertice' : str,
    'Metodo' : str    }


def csv_sniffer(fileobj):
    #Esta funcion averigua el delimitador y otras opciones del archivo csv automaticamente
    dialect = csv.Sniffer().sniff(fileobj.readline(), [',',';',' ', '\t'])
    fileobj.seek(0)
    return dialect
        
    
def transform_datatypes(filename):
    #Esta funcion lee el archivo csv de la fuente, luego ejecuta el sniffer para indicar el delimitador y crea un objeto DictReader
    #luego asigna el tipo de datos correspondiente a cada entrada de la fila
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter = csv_sniffer(csvfile).delimiter)
        Libreta = []
        for row in reader:
            fila = {}
            for i in reader.fieldnames:
                if i in data_types.keys():
                    fila[i]=data_types[i](row[i])
                else:
                    try:
                # Interpret the string as a Python literal
                        fila[i] = literal_eval(row[i])
                    except Exception:
                # If that doesn't work, assume it's an unquoted string
                        row[i]
            Libreta.append(fila)
    return Libreta

def obtener_vertices(Poligono):
    vertices = []
    puntos_vertices = []
    for observacion in Poligono.Puntos:
        if observacion.Poligono.lower() == Poligono.Nombre.lower():
            vertices.append(observacion.PO)
    for nombre in vertices:
        for punto in Punto.all:
            if punto.Nombre == nombre and punto.origen != True:
                puntos_vertices.append(punto)
    return puntos_vertices

def Plot_to_dxf(filename):

    drawing = dxf.drawing(name=filename)

    for i in Punto.all:
        drawing.modelspace.add(dxf.point((i.X, i.Y, i.Z)))
        if i.Nombre != None:
            drawing.modelspace.add(dxf.text(i.Nombre, insert=(i.X, i.Y, i.Z), color=2, alignpoint=(i.X, i.Y, i.Z)))
        
    def obtener_coordenadas_vertices(Poligono):
        vertices = []
        puntos_vertices = []
        coordenadas_vertices = []
        for observacion in Poligono.Puntos:
            if observacion.Poligono.lower() == Poligono.Nombre.lower():
                vertices.append(observacion.PO)
        for nombre in vertices:
            for punto in Punto.all:
                if punto.Nombre == nombre:
                    puntos_vertices.append(punto)
        for punto in puntos_vertices:
            coordenadas_vertices.append((punto.X, punto.Y, punto.Z))
        return coordenadas_vertices
                    
    def linetype(objeto):
        lt=''
        if type(objeto) is PoligonoAuxiliar:
            lt = 'DASHED'
        else:
            lt = 'CONTINUOUS'
        return lt
    
    for poligono in Poligono.all:
        p = drawing.modelspace.add(dxf.polyline(points = obtener_coordenadas_vertices(poligono), linetype=linetype(poligono), layer=poligono.Nombre, color=1))
        p.close()
            
    drawing.saveas(filename)

def buscar_nombres():
        nombres_poligonos = []
        for observacion in Observacion.all:
            if observacion.Poligono not in nombres_poligonos and observacion.Poligono !='':
                nombres_poligonos.append(observacion.Poligono)
        return nombres_poligonos

def crear_poligonos():

    def buscar_nombres():
        nombres_poligonos = []
        for observacion in Observacion.all:
            if observacion.Poligono not in nombres_poligonos and observacion.Poligono !='':
                nombres_poligonos.append(observacion.Poligono)
        return nombres_poligonos

    Nombres = buscar_nombres()
    
    for nombre in Nombres:
        if ('aux' or 'auxiliar') in nombre.lower():
            pol_aux = PoligonoAuxiliar(nombre, '')
            pol_aux.add_points()
            pol_aux.compensadas()            
        else:
            pol = Poligono(nombre, '')
            pol.add_points()

def distancia_horizontal(punto1, punto2):
	return np.sqrt((punto1.X-punto2.X)**2+(punto1.Y-punto2.Y)**2)
	
def distancia_3d(punto1, punto2):
	return np.sqrt((punto1.X-punto2.X)**2+(punto1.Y-punto2.Y)**2+(punto1.Z-punto2.Z)**2)

def direccion(punto1, punto2, formato='rumbo', decimales_segundos=0):
	delta_x = punto2.X-punto1.X
	delta_y = punto2.Y-punto1.Y
	hemisferio_ns = ''
	hemisferio_ew = ''
	angulo = deci2sexa(np.degrees(np.arctan(abs(delta_x)/abs(delta_y))),pre=decimales_segundos)
	
	if delta_y > 0:
		hemisferio_ns = 'N'
	else:
		hemisferio_ns = 'S'
		
	if delta_x > 0:
		hemisferio_ew = 'E'
	else:
		hemisferio_ew = 'W'
		
	if formato.lower() == 'rumbo':
		return "{0} {1:02d}°{2:02d}'{3:02d}\" {4}".format(hemisferio_ns, int(angulo[1]), int(angulo[2]), int(angulo[3]), hemisferio_ew)
	elif formato.lower() == 'azimut':
		return "{0:02d}°{1:02d}'{2:02d}\"".format(int(angulo[1]), int(angulo[2]), int(angulo[3]))

def libreta_final(poligono, formato='rumbo'):
	vertices = obtener_vertices(poligono)

        def str_direccion():
            if formato.lower() == 'rumbo':
                direccion = 'RUMBO'
            else:
                direccion = 'AZIMUT'
            return direccion
	
	def generar_entrada(vertice):                
		anterior = vertices.index(vertice)-1
		EST = vertices[anterior].Nombre
		PO = vertice.Nombre
		Direccion = direccion(vertices[anterior], vertice, formato)
		DH = distancia_horizontal(vertices[anterior], vertice)
		return {'EST':EST, 'PO':PO, str_direccion():Direccion, 'DISTANCIA(m)':'{:.04f}'.format(DH)}
        		
	Libreta_Final = []
	for vertice in vertices:
		Libreta_Final.append(generar_entrada(vertice))
	return Libreta_Final

def generar_libreta_totales(Z=True):
    Libreta = []
    for punto in Punto.all:
        datos_punto = {}
        datos_punto['Punto'] = punto.Nombre
        datos_punto['X'] = punto.X
        datos_punto['Y'] = punto.Y
        if Z == True:
            datos_punto['Z'] = punto.Z
        Libreta.append(datos_punto)
    return Libreta

def guardar_csv(filename, fuente_datos, fields):
    with open(filename, 'wb') as output_file:
        fieldnames = fields
        writer = csv.DictWriter(output_file, fieldnames=fieldnames,extrasaction='ignore', dialect='excel')
        writer.writeheader()
        writer.writerows(fuente_datos)