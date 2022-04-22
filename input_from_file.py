import numpy as np
import csv
from reader2 import data_types
from Topografia import *
from dxfwrite import DXFEngine as dxf

def importar_puntos(filename):
    
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        Libreta = []
        for row in reader:
            fila = []
            for i in reader.fieldnames:
                fila.append(data_types[i](row[i]))
            Libreta.append(fila)
        Libreta.insert(0, reader.fieldnames) 
        return Libreta
    
def add_points(Obj_poligono):
    puntos = []
    for i in Observacion.all:
        if i.Poligono.lower() == Obj_poligono.Nombre.lower():
            puntos.append(i)
    Obj_poligono.Puntos = puntos