from flask import Flask, jsonify, request
from flask_cors import CORS

from ejercicio1_mutex import run_mutex_simulation
from ejercicio2_semaforo import run_gimnasio_simulation
from ejercicio3_productor_consumidor import run_panaderia_simulation
from ejercicio4_lectores_escritores import run_lectores_escritores_simulation
from ejercicio5_barrera import run_barrera_simulation

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return jsonify({
        "proyecto": "APE 3 - Sistemas Distribuidos",
        "endpoints": [
            "GET /ej1/mutex?n_hilos=5&m_ventas=200&usar_mutex=true",
            "GET /ej2/semaforo?n_maquinas=3&n_atletas=8",
            "GET /ej3/panaderia?capacidad=5&n_panes=10&n_clientes=3",
            "GET /ej4/lectores_escritores?n_lectores=5&n_escritores=2&iteraciones=3",
            "GET /ej5/barrera?n_hilos=5"
        ]
    })


@app.route("/ej1/mutex")
def ej1_mutex():
    n_hilos = int(request.args.get("n_hilos", 5))
    m_ventas = int(request.args.get("m_ventas", 200))
    usar_mutex_str = request.args.get("usar_mutex", "true").lower()
    usar_mutex = usar_mutex_str == "true"

    # Limitar para demo rápida
    n_hilos = min(n_hilos, 10)
    m_ventas = min(m_ventas, 500)

    resultado = run_mutex_simulation(n_hilos=n_hilos, m_ventas=m_ventas, usar_mutex=usar_mutex)
    return jsonify(resultado)


@app.route("/ej2/semaforo")
def ej2_semaforo():
    n_maquinas = int(request.args.get("n_maquinas", 3))
    n_atletas = int(request.args.get("n_atletas", 8))

    n_maquinas = min(n_maquinas, 10)
    n_atletas = min(n_atletas, 15)

    resultado = run_gimnasio_simulation(n_maquinas=n_maquinas, n_atletas=n_atletas)
    return jsonify(resultado)


@app.route("/ej3/panaderia")
def ej3_panaderia():
    capacidad = int(request.args.get("capacidad", 5))
    n_panes = int(request.args.get("n_panes", 10))
    n_clientes = int(request.args.get("n_clientes", 3))

    capacidad = min(capacidad, 10)
    n_panes = min(n_panes, 20)
    n_clientes = min(n_clientes, 5)

    resultado = run_panaderia_simulation(capacidad=capacidad, n_panes=n_panes, n_clientes=n_clientes)
    return jsonify(resultado)


@app.route("/ej4/lectores_escritores")
def ej4_lectores_escritores():
    n_lectores = int(request.args.get("n_lectores", 5))
    n_escritores = int(request.args.get("n_escritores", 2))
    iteraciones = int(request.args.get("iteraciones", 3))

    n_lectores = min(n_lectores, 8)
    n_escritores = min(n_escritores, 4)
    iteraciones = min(iteraciones, 5)

    resultado = run_lectores_escritores_simulation(
        n_lectores=n_lectores,
        n_escritores=n_escritores,
        iteraciones=iteraciones
    )
    return jsonify(resultado)


@app.route("/ej5/barrera")
def ej5_barrera():
    n_hilos = int(request.args.get("n_hilos", 5))
    n_hilos = min(n_hilos, 10)

    resultado = run_barrera_simulation(n_hilos=n_hilos)
    return jsonify(resultado)


if __name__ == "__main__":
    print("=" * 50)
    print("  APE 3 - Sistemas Distribuidos - Backend")
    print("  Servidor corriendo en http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000, threaded=True)