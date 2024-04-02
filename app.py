import numpy as np
from flask import Flask
from flask import render_template
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Datos del problema
MTOW = 128500  # kg
OEW = 65400     # kg
MPL = 30300    # kg
MFW = 52200    # kg
K = 25800       # km

#Puntos caracteristicos del Diagrama PL-R
class PuntoCaracteristico(object):
    def __init__(self, nombre, PL, TOW, FW, OEW, K):
        self.nombre = nombre
        self.PL = PL
        self.TOW = TOW
        self.FW = FW
        self.OEW = OEW
        self.K = K
        self.x = self.K * np.log((self.OEW + self.FW + self.PL) / (self.OEW + self.PL))
        self.y = self.PL 

    def __str__(self):
        mistr = f"Punto: ({self.x}, {self.y})"
        return mistr 

# Definir los valores de PL, TOW y FW para cada punto:
valores_puntos = [
    {'nombre': ' A', 'PL': MPL, 'TOW': OEW + MPL, 'FW': 0},
    {'nombre': ' B', 'PL': MPL, 'TOW': MTOW, 'FW': MTOW - OEW - MPL},
    {'nombre': ' C', 'PL': MTOW - OEW - MFW, 'TOW': MTOW, 'FW': MFW},
    {'nombre': ' D', 'PL': 0, 'TOW': MFW + OEW, 'FW': MFW}
]

colores = ['b', 'g', 'r', 'c']  
puntos = []
for i, valores in enumerate(valores_puntos):
    puntos.append(PuntoCaracteristico(valores['nombre'], valores['PL'], valores['TOW'], valores['FW'], OEW, K))
    puntos[-1].color = colores[i] 

#Unimos los puntos caracteristicos que definen el diagrama mediante una funcion a trozos
def funcion_a_trozos(x):
    if x <= puntos[0].x:  
        return puntos[0].y
    elif x >= puntos[-1].x: 
        return puntos[-1].y
    else:
        for i in range(len(puntos) - 1):
            if puntos[i].x <= x <= puntos[i + 1].x:  
                m = (puntos[i + 1].y - puntos[i].y) / (puntos[i + 1].x - puntos[i].x)
                b = puntos[i].y - m * puntos[i].x
                return m * x + b


x_values = np.linspace(puntos[0].x, puntos[-1].x, 100)


y_values = [funcion_a_trozos(x) for x in x_values]


# Crear la aplicación Flask
app = Flask(__name__)


@app.route('/')
def index():
    
    plt.plot(x_values, y_values, 'r-')
    for punto in puntos:
        plt.plot(punto.x, punto.y, marker='o', color=punto.color, label=punto.nombre)
        plt.text(punto.x, punto.y, punto.nombre, fontsize=8, ha='right', va='bottom')
    plt.xlabel('Alcance (km)')
    plt.ylabel('Carga de Pago (kg)')
    plt.title('DIAGRAMA PL-R')
    plt.legend()
    plt.grid(True)
    
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode()
    
  
    return render_template('index.html', img_base64=img_base64)

if __name__ == '__main__':
    app.run(debug=True)
