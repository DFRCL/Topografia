from Tkinter import *
from tkFileDialog   import askopenfilename
from tkFileDialog import asksaveasfilename
import gpxpy
import gpxpy.gpx
import utm
import pyproj 
from script_conservacion_azimut import *


GTM_WGS84 = pyproj.Proj("+proj=tmerc +lat_0=0 +lon_0=-90.5 +k=0.9998 +x_0=500000 +y_0=0 +ellps=WGS84 +units=m +no_defs")

def geograficas_a_proyeccion(latitud, longitud, formato = 'UTM'):
    if formato == 'UTM':
        return utm.from_latlon(latitud, longitud)
    if formato == 'GTM':
        return GTM_WGS84(longitud, latitud)

class PuntoGeodesico(object):
    #Punto con coordenadas geodésicas en cualquier formato (UTM, geográficas, etc.)

    @property
    def Northing(self):
        return self._Northing
    @Northing.setter
    def Northing(self, Value):
        self._Northing = Value

    @property
    def Easting(self):
        return self._Northing
    @Northing.setter
    def Easting(self, Value):
        self._Northing = Value

class Track(object):
    all = []
    
    def __init__(self, Nombre = None, Descripcion = None, Puntos=None, Closed=False):
        self.Nombre = Nombre
        self.Descripcion = Descripcion
        self.Puntos = Puntos
        self.Closed = Closed
        Track.all.append(self)

def parse_gpx(filename, formato='UTM', puntos_tracks=True):
    with open(filename, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        Datos_gpx = {}
        Waypoints = []
        Tracks = []

        def parse_waypoint(waypoint):
            wpt = {}
            PROYECCION = geograficas_a_proyeccion(waypoint.latitude, waypoint.longitude, formato)
            
            wpt['Nombre'] = waypoint.name
            wpt['X'] = PROYECCION[0]
            wpt['Y'] = PROYECCION[1]
            wpt['Z'] = waypoint.elevation
            return Punto(**wpt)

        def parse_track(track, puntos_tracks_opt):
            trck = {}
            trck['Nombre'] = track.name
            trck['Descripcion'] = track.description
            puntos = []
            coordenadas_puntos = []
            for segment in track.segments:
                for waypoint in segment.points:          
                    wpt = {}
                    PROYECCION = geograficas_a_proyeccion(waypoint.latitude, waypoint.longitude, formato)
                    
                    wpt['Nombre'] = waypoint.name
                    wpt['X'] = PROYECCION[0]
                    wpt['Y'] = PROYECCION[1]
                    wpt['Z'] = waypoint.elevation
                    if puntos_tracks_opt:
                        punto = Punto(**wpt)
                    else:
                        punto = wpt
                    puntos.append(punto)

                    coordenadas_puntos.append((wpt['X'],wpt['Y'],wpt['Z']))
            trck['Puntos'] = puntos

            trck['coordenadas_puntos'] = coordenadas_puntos
            Track(Nombre = trck['Nombre'], Descripcion = trck['Descripcion'], Puntos = trck['coordenadas_puntos'], Closed=False)
            
            return trck

        for waypoint in gpx.waypoints:
            Waypoints.append(parse_waypoint(waypoint))

        
        for track in gpx.tracks:
            Tracks.append(parse_track(track, puntos_tracks))
            
        Datos_gpx['Waypoints'] = Waypoints
        Datos_gpx['Tracks'] = Tracks
        
        return Datos_gpx

def Plot_gpx_to_dxf(filename):

    drawing = dxf.drawing(name=filename)

    for i in Punto.all:
        drawing.modelspace.add(dxf.point((i.X, i.Y, i.Z),layer='PUNTOS'))
        if i.Nombre != None:
            drawing.modelspace.add(dxf.text(i.Nombre, insert=(i.X, i.Y, i.Z), color=2, alignpoint=(i.X, i.Y, i.Z), layer='ROTULOS PUNTOS'))    
    
    for track in Track.all:
        p = drawing.modelspace.add(dxf.polyline(points = track.Puntos, linetype='CONTINUOUS',layer = 'TRACK '+str(track.Nombre).replace(':',' '), color=4))
        if track.Closed:
            p.close()
            
    drawing.saveas(filename)

def generar_salida(Z=True):
    Libreta = []
    for punto in Punto.all:
        datos_punto = {}
        #datos_punto['Punto'] = punto.Nombre
        datos_punto['X'] = punto.X
        datos_punto['Y'] = punto.Y
        if Z == True:
            datos_punto['Z'] = punto.Z
        Libreta.append(datos_punto)
    return Libreta

def generar_salida_geograficas(filename, Z=True):
    with open(filename, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        Libreta = []
        for waypoint in gpx.waypoints:
            datos_punto = {}
            #datos_punto['Punto'] = punto.Nombre
            datos_punto['Latitud'] = waypoint.latitude
            datos_punto['Longitud'] = waypoint.longitude
            if Z == True:
                datos_punto['Z'] = waypoint.elevation
            Libreta.append(datos_punto)
        for track in gpx.tracks:
            for segment in track.segments:
                for waypoint in segment.points:
                    datos_punto = {}
                    #datos_punto['Punto'] = punto.Nombre
                    datos_punto['Latitud'] = waypoint.latitude
                    datos_punto['Longitud'] = waypoint.longitude
                    if Z == True:
                        datos_punto['Z'] = waypoint.elevation
                    Libreta.append(datos_punto)
        return Libreta

class Aplicacion(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.track_points = BooleanVar()
        self.gpx_filename = None
        
        Label(master, text="Importar GPX").grid(row=0,columnspan=2)

        Button(master, text="Importar archivo .gpx",command = self.procesar_gpx).grid(row=1, column=0)
        
        Checkbutton(master, text="Importar puntos de tracks", variable=self.track_points).grid(row=1,column=1)
        
        Label(master, text="Exportar a DFX").grid(row=2, column = 0)

        Button(master, text="Guardar como DXF (AutoCAD)", command = self.guardar_dxf).grid(row=4, column = 0, rowspan=2)

        Label(master, text="Exportar a CSV").grid(row=2, column = 1)

        Button(master, text="Guardar coordenadas geográficas", command = self.exportar_geograficas).grid(row=4, column = 1)

        Button(master, text="Guardar coordenadas de proyección", command = self.exportar_coordenadas).grid(row=5, column = 1)

    def askopenfilename(self):
        # get filename
        filename = askopenfilename(filetypes=[('GPX','.gpx'),('All files','.*')], defaultextension='.gpx')
        # open file on your own
        self.gpx_filename = filename
        if filename:
            return self.gpx_filename

    def procesar_gpx(self):
        return parse_gpx(self.askopenfilename(),puntos_tracks=self.track_points.get())

    def guardar_dxf(self):
        return Plot_gpx_to_dxf(asksaveasfilename(filetypes=[('DXF','.dxf'),('All files','.*')], defaultextension='.dxf'))

    def exportar_geograficas(self):
        guardar_csv(asksaveasfilename(defaultextension='.csv',filetypes=[('CSV','.csv'),('All files','.*')]), generar_salida_geograficas(self.gpx_filename), ['Latitud','Longitud', 'Z'])

    def exportar_coordenadas(self):
        guardar_csv(asksaveasfilename(defaultextension='.csv',filetypes=[('CSV','.csv'),('All files','.*')]), generar_libreta_totales(), ['X','Y','Z'])
if __name__=='__main__':
    root = Tk()
    app = Aplicacion(master=root)
    app.mainloop()