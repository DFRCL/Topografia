from angles import deci2sexa

def distancia_horizontal(punto1, punto2):
	return sqrt((punto1.X-punto2.X)**2+(punto1.Y-punto2.Y)**2)
	
def distancia_3d(punto1, punto2):
	return sqrt((punto1.X-punto2.X)**2+(punto1.Y-punto2.Y)**2+(punto1.Z-punto2.Z)**2)

def direccion(punto1, punto2, formato='rumbo', decimales=0):
	delta_x = punto1.X-punto2.X
	delta_y = punto1.Y-punto2.Y
	hemisferio_ns = ''
	hemisferio_ew = ''
	angulo = deci2sexa(np.degrees(np.arctan(abs(delta_x)/abs(delta_y))),pre=decimales)
	
	if delta_x > 0:
		hemisferio_ns = 'N'
	else:
		hemisferio_ns = 'S'
		
	if delta_y > 0:
		hemisferio_ew = 'E'
	else:
		hemisferio_ew = 'W'
		
	if formato.lower() == 'rumbo':
		return '{0} {1:02d}°{2:02d}\'{3:02d}\" {4}'.format(hemisferio_ns, angulo[1], angulo[2], angulo[3], hemisferio_ew)
	elif formato.lower() == 'azimut':
		return '{0:02d}°{1:02d}\'{2:02d}\"'.format(angulo[1], angulo[2], angulo[3])

def libreta_final(poligono, formato='rumbo'):
	vertices = obtener_vertices(poligono)
	
	def generar_entrada(vertice):
		anterior = vertices.index(vertice)-1
		EST = vertices[anterior].Nombre
		PO = vertice.Nombre
		Direccion = direccion(vertices[anterior], vertice, formato)
		DH = distancia_horizontal(vertices[anterior], vertice)
		return {'EST':EST, 'PO':PO, 'Direccion':Direccion, 'DH':DH}
        if formato == 'rumbo':
            direccion = 'RUMBO'
        else:
            direccion = 'AZIMUT'		
	Libreta_Final = []
	for vertice in vertices:
		Libreta_Final.append(generar_entrada(vertice))
	fieldnames = ['EST','PO',direccion, 'DISTANCIA(m)']
	return Libreta_Final
	
def generar_libreta_totales(Z=True, Descripcion=True):
    Libreta = []
    Formato = {'PENZD', 'PNEZD', ''}
    for punto in Punto.all:
        datos_punto = {}
        datos_punto['Punto'] = punto.Nombre
        datos_punto['X'] = punto.X
        datos_punto['Y'] = punto.Y
        if Z == True:
            datos_punto['Z'] = punto.Z
        if Descripcion == True:
            datos_punto['Descripcion']
        Libreta.append(datos_punto)
    return Libreta
		
	