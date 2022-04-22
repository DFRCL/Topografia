def Plot_to_dxf(filename):

    drawing = dxf.drawing(name=filename)

    for i in Punto.all:
        drawing.modelspace.add(dxf.point((i.X, i.Y, i.Z)))
        drawing.modelspace.add(dxf.text(i.Nombre, insert=(i.X, i.Y), color=2))

    """for poligono in Poligono.all:
        vertices = []
        for punto in i.Puntos:
            vertices.append((punto.X, punto.Y, punto.Z))
        drawing.modelspace.add(dxf.polyline(points = vertices, linetype='DASHED', layer = i.Nombre))"""

    
    drawing.save()