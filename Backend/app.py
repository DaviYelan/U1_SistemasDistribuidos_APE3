import json
import queue
import threading
import time

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from ejercicio1_mutex import run_mutex_simulation
from ejercicio2_semaforo import run_gimnasio_simulation
from ejercicio3_productor_consumidor import run_panaderia_simulation
from ejercicio4_lectores_escritores import run_lectores_escritores_simulation
from ejercicio5_barrera import run_barrera_simulation

app = Flask(__name__)
CORS(app)


# ─── SSE helpers ─────────────────────────────────────────────────────────────

def sse_stream(sim_fn, **kwargs):
    """
    Crea una cola de eventos, lanza la simulación en un hilo aparte
    inyectando emit_fn y done_fn, y hace streaming SSE al cliente.

    Protocolo:
      data: <json>\n\n           → evento de log
      data: __DONE__<json>\n\n   → resultado final, cierra el stream
      data: __ERROR__<json>\n\n  → error, cierra el stream
    """
    q = queue.Queue()

    def emit(event_dict):
        q.put(("log", event_dict))

    def done(result_dict):
        q.put(("done", result_dict))

    def run():
        try:
            sim_fn(emit_fn=emit, done_fn=done, **kwargs)
        except Exception as exc:
            q.put(("error", {"mensaje": str(exc)}))

    threading.Thread(target=run, daemon=True).start()

    def generate():
        while True:
            try:
                kind, payload = q.get(timeout=30)
            except queue.Empty:
                yield "data: __TIMEOUT__\n\n"
                break

            if kind == "log":
                yield f"data: {json.dumps(payload)}\n\n"
            elif kind == "done":
                yield f"data: __DONE__{json.dumps(payload)}\n\n"
                break
            elif kind == "error":
                yield f"data: __ERROR__{json.dumps(payload)}\n\n"
                break

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ─── Rutas ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return jsonify({"proyecto": "APE 3 - Sistemas Distribuidos (SSE)"})


@app.route("/ej1/mutex")
def ej1_mutex():
    n_hilos    = min(int(request.args.get("n_hilos",   5)),  10)
    m_ventas   = min(int(request.args.get("m_ventas", 200)), 500)
    usar_mutex = request.args.get("usar_mutex", "true").lower() == "true"
    return sse_stream(run_mutex_simulation,
                      n_hilos=n_hilos, m_ventas=m_ventas, usar_mutex=usar_mutex)


@app.route("/ej2/semaforo")
def ej2_semaforo():
    n_maquinas = min(int(request.args.get("n_maquinas", 3)), 10)
    n_atletas  = min(int(request.args.get("n_atletas",  8)), 15)
    return sse_stream(run_gimnasio_simulation,
                      n_maquinas=n_maquinas, n_atletas=n_atletas)


@app.route("/ej3/panaderia")
def ej3_panaderia():
    capacidad  = min(int(request.args.get("capacidad",  5)), 10)
    n_panes    = min(int(request.args.get("n_panes",   10)), 20)
    n_clientes = min(int(request.args.get("n_clientes", 3)),  5)
    return sse_stream(run_panaderia_simulation,
                      capacidad=capacidad, n_panes=n_panes, n_clientes=n_clientes)


@app.route("/ej4/lectores_escritores")
def ej4_lectores_escritores():
    n_lectores   = min(int(request.args.get("n_lectores",   5)), 8)
    n_escritores = min(int(request.args.get("n_escritores", 2)), 4)
    iteraciones  = min(int(request.args.get("iteraciones",  3)), 5)
    return sse_stream(run_lectores_escritores_simulation,
                      n_lectores=n_lectores, n_escritores=n_escritores,
                      iteraciones=iteraciones)


@app.route("/ej5/barrera")
def ej5_barrera():
    n_hilos = min(int(request.args.get("n_hilos", 5)), 10)
    return sse_stream(run_barrera_simulation, n_hilos=n_hilos)


if __name__ == "__main__":
    print("=" * 50)
    print("  APE 3 · Backend SSE · http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000, threaded=True)