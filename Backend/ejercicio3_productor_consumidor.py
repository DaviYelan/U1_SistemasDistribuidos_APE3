import threading
import time
import random

class SemaforoConteo:
    def __init__(self, valor):
        self.contador = valor
        self.cond = threading.Condition()

    def esperar(self):
        with self.cond:
            while self.contador == 0:
                self.cond.wait()
            self.contador -= 1

    def senial(self):
        with self.cond:
            self.contador += 1
            self.cond.notify()

def run_panaderia_simulation(capacidad=5, n_panes=10, n_clientes=3):
    espacios_vacios = SemaforoConteo(capacidad)
    panes_listos = SemaforoConteo(0)
    mutex_vitrina = threading.Lock()

    vitrina = []  # Buffer compartido
    logs = []
    logs_lock = threading.Lock()
    panes_producidos = [0]
    panes_consumidos = [0]
    done_event = threading.Event()

    tipos_pan = ["🥖 Baguette", "🍞 Pan Blanco", "🥐 Croissant", "🧁 Muffin", "🥯 Bagel"]

    def panadero():
        for i in range(n_panes):
            tipo = random.choice(tipos_pan)
            time.sleep(random.uniform(0.1, 0.4))  # Tiempo de horneado

            espacios_vacios.esperar()          # ¿Cabe en la vitrina?
            with mutex_vitrina:                # Abrir vitrina
                vitrina.append(tipo)
                panes_producidos[0] += 1
                snap = list(vitrina)

            with logs_lock:
                logs.append({
                    "actor": "👨‍🍳 Panadero",
                    "accion": f"Hornea y coloca {tipo}",
                    "vitrina": snap,
                    "ocupacion": len(snap),
                    "capacidad": capacidad,
                    "timestamp": round(time.time() % 1000, 3)
                })

            panes_listos.senial()              # Avisar al cliente

        done_event.set()

    def cliente(cliente_id):
        while True:
            panes_listos.esperar()             # ¿Hay pan?

            with mutex_vitrina:                # Abrir vitrina
                if not vitrina:
                    espacios_vacios.senial()
                    continue
                pan = vitrina.pop(0)
                panes_consumidos[0] += 1
                snap = list(vitrina)

            with logs_lock:
                logs.append({
                    "actor": f"🧑‍💼 Cliente {cliente_id}",
                    "accion": f"Compra {pan}",
                    "vitrina": snap,
                    "ocupacion": len(snap),
                    "capacidad": capacidad,
                    "timestamp": round(time.time() % 1000, 3)
                })

            espacios_vacios.senial()           # Avisar al panadero

            time.sleep(random.uniform(0.05, 0.2))

            if done_event.is_set() and panes_consumidos[0] >= n_panes:
                break

    inicio = time.time()
    hilos = [threading.Thread(target=panadero)]
    for c in range(n_clientes):
        hilos.append(threading.Thread(target=cliente, args=(c + 1,)))

    for t in hilos:
        t.daemon = True
        t.start()

    hilos[0].join(timeout=30)
    # Esperar que clientes consuman todo
    timeout = time.time() + 10
    while panes_consumidos[0] < n_panes and time.time() < timeout:
        time.sleep(0.05)

    duracion = round(time.time() - inicio, 3)
    correcto = panes_producidos[0] == n_panes and panes_consumidos[0] == n_panes

    return {
        "capacidad_vitrina": capacidad,
        "n_panes_objetivo": n_panes,
        "panes_producidos": panes_producidos[0],
        "panes_consumidos": panes_consumidos[0],
        "n_clientes": n_clientes,
        "correcto": correcto,
        "duracion_segundos": duracion,
        "logs": sorted(logs, key=lambda x: x["timestamp"])[:40],
        "conclusion": (
            f"✅ Productor-Consumidor correcto. Producidos={panes_producidos[0]}, Consumidos={panes_consumidos[0]}"
            if correcto else
            f"⚠️ Incompleto. Producidos={panes_producidos[0]}, Consumidos={panes_consumidos[0]}"
        )
    }