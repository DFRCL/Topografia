import csv
from reader2 import data_types


def csv_sniffer(fileobj):
    #Esta funcion averigua el delimitador y otras opciones del archivo csv automaticamente
    dialect = csv.Sniffer().sniff(fileobj.readline(), [',',';',' ', '\t'])
    fileobj.seek(0)
    return dialect
        
    
def transform_datatypes(filename):
    #Esta funcion lee el archivo csv de la fuente, luego ejecuta el sniffer para indicar el delimitador y crea un objeto DictReader
    #luego asigna el tipo de datos correspondiente a cada entrada de la fila
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter = csv_sniffer(csvfile).delimiter)
        Libreta = []
        for row in reader:
            fila = {}
            for i in reader.fieldnames:
                if i in data_types.keys():
                    fila[i]=data_types[i](row[i])
                else:
                    try:
                # Interpret the string as a Python literal
                        fila[i] = literal_eval(row[i])
                    except Exception:
                # If that doesn't work, assume it's an unquoted string
                        row[i]
            Libreta.append(fila)
    return Libreta