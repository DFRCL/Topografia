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