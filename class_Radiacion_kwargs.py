class Radiacion(object):
    all = []
    
    def Parciales(self):
        y = self.Distancia*np.cos(np.radians(self.Azimut))
        x = self.Distancia*np.sin(np.radians(self.Azimut))
        return x,y

    def __init__(self, **kwargs):
        self.PO = kwargs.get('PO')
        self.EST = kwargs.get('EST')
        self.Descripcion = kwargs.get('Descripcion')
        self.Poligono = kwargs.get('Poligono')
        self.Azimut = kwargs.get('Grados')+(kwargs.get('Minutos')/60)+(kwargs.get('Segundos')/3600)
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