from dxfwrite import DXFEngine as dxf
from Topografia import *


Levantamiento1 = Levantamiento('Levantamiento 1', 'Douglas Castillo', 'Ciudad', '30/11/2016', '7:00', 'Teodolito', 'Conservacion de Azimut')
Libreta = [['0','1','Arbol','Poligono1',60,50], ['1','2','Arbol','Poligono1',180,50], ['2','0','Arbol','Poligono1',300,50], ['2','2.1','Arbol','Poligono1',300,50]]
Observacion1 = Radiacion('0','1','Arbol','Poligono1',60,50)
Observacion2 = Radiacion('1','2','Arbol','Poligono1',180,50)
Observacion3 = Radiacion('2','0','Arbol','Poligono1',300,50)
Observacion4 = Radiacion('2','2.1','Arbol','Poligono1',10,50)
Observacion5 = Cilindricas('2','2.3','Arbol','Poligono1',20,50, 1)
Observacion6 = Esfericas('2','2.4','Arbol','Poligono1',25,50, 88)
Observacion7 = Taquimetria('2', '2.5', 'Acera', 'Poligono1', 30, 2, 1.5, 1, 88)
Observacion8 = Taquimetria3D('2', '2.6', 'Acera', 'Poligono1', 45, 2, 1.5, 1, 88, 1.45)
Observacion9 = Cartesiana_relativa('2', '2.7', 'Esquina', 10, 5, 2)

Punto('0',0 , 0, 0)

for i in Observacion.all:
    Totales(i)
    
Plot()

drawing = dxf.drawing(name='test.dxf')

for i in Punto.all:
    drawing.modelspace.add(dxf.point((i.X, i.Y, i.Z)))
    drawing.modelspace.add(dxf.text(i.Nombre, insert=(i.X, i.Y), color=2))


Ancho_hoja = 0.2794
Largo_hoja = 0.2159
#Cajetin
drawing.paperspace.add(dxf.viewport(center_point=(Ancho_hoja/2, Largo_hoja/2+0.02),
        # viewport width in paper space
        width=Largo_hoja-0.04,
        # viewport height in paper space
        height=Ancho_hoja-0.02))


#set value
drawing.header['$ANGBASE'] = 30

#get value
version = drawing.header['$ACADVER'].value

# for 2D/3D points use:
minx, miny, minz = drawing.header['$EXTMIN'].tuple

#set paper space size
drawing.header['$PEXTMAX'] = (0.2794, 0.2159, 0)
drawing.header['$PEXTMIN'] = (0, 0, 0)
drawing.header['$LUNITS'] = 1

drawing.save()