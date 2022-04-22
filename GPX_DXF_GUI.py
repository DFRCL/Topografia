# -*- coding: utf-8 -*-
from tkinter import *
from gpx_parse import *
from tkFileDialog   import askopenfilename
from tkFileDialog import asksaveasfilename

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