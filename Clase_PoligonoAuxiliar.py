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
        for i in Radiacion.all:
            if i.Poligono.lower() == self.Nombre.lower():
                puntos.append(i)
        self.Puntos = puntos

    def __init__(self, Nombre, Descripcion):
        self.Nombre = Nombre
        self.Descripcion = Descripcion
        Poligono.__init__(self, Nombre, Descripcion)
        #self.Estaciones = 0