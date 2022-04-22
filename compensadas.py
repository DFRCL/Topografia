from Topografia3 import *

Observacion.all = []
Levantamiento1 = Levantamiento('Levantamiento 1', 'Douglas Castillo', 'Ciudad', '30/11/2016', '7:00', 'Teodolito', 'Conservacion de Azimut')

Punto('0', 0, 0, 0)
#Libreta = [['0','1','Arbol','Poligono1',60,50], ['1','2','Arbol','Poligono1',180,50], ['2','0','Arbol','Poligono1',300,50], ['2','2.1','Arbol','Poligono1',300,50]]
Observacion1 = Radiacion('0','1','Arbol','Poligono1',60,50)
Observacion2 = Radiacion('1','2','Arbol','Poligono1',180,50)
Observacion3 = Radiacion('2','0','Arbol','Poligono1',300,50)
Observacion4 = Radiacion('2','2.1','Arbol','Poligono1',10,50)
Observacion5 = Cilindricas('2','2.3','Arbol','Poligono1',20,50, 1)
Observacion6 = Esfericas('2','2.4','Arbol','Poligono1',25,50, 88)
Observacion7 = Taquimetria('2', '2.5', 'Acera', 'Poligono1', 30, 2, 1.5, 1, 88)
Observacion8 = Taquimetria3D('2', '2.6', 'Acera', 'Poligono1', 45, 2, 1.5, 1, 88, 1.45)
Observacion9 = Cartesiana_relativa('2', '2.7', 'Esquina', 10, 5, 2)

class Poligono(object):
    all = []
    
    def __init__(self, Nombre, Descripcion):
        self.Nombre=Nombre
        self.Puntos=[]
        self.Descripcion=Poligono
        Poligono.all.append(self)
        
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
            else:
                return -1
            
        def compensar_eje(punto, eje):
            s = signo(eje)
            fc_eje = fc(eje)
            
            return getattr(punto, eje)+(s*abs(getattr(punto, eje)*fc_eje))
            
            
            
        for punto in self.Puntos:
            punto.x = compensar_eje(punto, 'x')
            punto.y = compensar_eje(punto, 'y')
            punto.z = compensar_eje(punto, 'z')
    
    def __init__(self, Nombre, Descripcion):
        Poligono.__init__(self, Nombre, Descripcion)
        #self.Estaciones = 0


        
PoligonoAux = PoligonoAuxiliar('Poligono Auxiliar', 'Poligonito')

PoligonoAux.Puntos = [Observacion1, Observacion2, Observacion3, Observacion5]

print 'sin compensar \n'
for i in PoligonoAux.Puntos:
    print i.x, i.y, i.z
    
print '\n'
PoligonoAux.compensadas()
print 'compensadas \n'
for i in PoligonoAux.Puntos:
    print i.x, i.y, i.z

for i in Observacion.all:
    Totales(i)
    
for i in Punto.all:
    print i