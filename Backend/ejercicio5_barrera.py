import threading
import time
import random


class BarreraSincronizacion:
    def __init__(self, n_total):
        self.n_total = n_total
        self.contador = 0
        self.var_cond = threading.Condition(threading.Lock())

    def llegar(self, hilo_id, emit_fn):
        with self.var_cond:
            self.contador += 1
            llegada = self.contador

            emit_fn({
                "hilo": hilo_id,
                "evento": f"🚩 Llegó a la barrera ({llegada}/{self.n_total})",
                "fase": "BARRERA",
                "timestamp": round(time.time() % 1000, 4),
            })

            if self.contador == self.n_total:
                emit_fn({
                    "hilo": hilo_id,
                    "evento": "🔔 ¡ÚLTIMO EN LLEGAR! Despertando a todos...",
                    "fase": "BROADCAST",
                    "timestamp": round(time.time() % 1000, 4),
                })
                self.var_cond.notify_all()
            else:
                while self.contador < self.n_total:
                    self.var_cond.wait()


def run_barrera_simulation(emit_fn, done_fn, n_hilos=5):
    barrera = BarreraSincronizacion(n_hilos)
    fase1_tiempos = {}
    fase2_inicios = {}
    data_lock = threading.Lock()

    def proceso(hilo_id):
        duracion_fase1 = random.uniform(1.5, 2.0)

        emit_fn({
            "hilo": hilo_id,
            "evento": f"▶️ Inicia Fase 1 (durará {duracion_fase1:.2f}s)",
            "fase": "FASE_1",
            "timestamp": round(time.time() % 1000, 4),
        })

        time.sleep(duracion_fase1)

        with data_lock:
            fase1_tiempos[hilo_id] = time.time()

        emit_fn({
            "hilo": hilo_id,
            "evento": f"✅ Completó Fase 1 en {duracion_fase1:.2f}s",
            "fase": "FASE_1_FIN",
            "timestamp": round(time.time() % 1000, 4),
        })

        barrera.llegar(hilo_id, emit_fn)

        with data_lock:
            fase2_inicios[hilo_id] = time.time()

        emit_fn({
            "hilo": hilo_id,
            "evento": "🚀 Inicia Fase 2",
            "fase": "FASE_2",
            "timestamp": round(time.time() % 1000, 4),
        })

        time.sleep(random.uniform(1.5, 2.0))

        emit_fn({
            "hilo": hilo_id,
            "evento": "🏁 Completó Fase 2",
            "fase": "FASE_2_FIN",
            "timestamp": round(time.time() % 1000, 4),
        })

    inicio = time.time()
    hilos = []
    for i in range(n_hilos):
        t = threading.Thread(target=proceso, args=(i + 1,))
        hilos.append(t)
        t.start()
    for t in hilos:
        t.join()

    duracion = round(time.time() - inicio, 3)
    max_fin_fase1   = max(fase1_tiempos.values()) if fase1_tiempos else 0
    min_inicio_fase2 = min(fase2_inicios.values()) if fase2_inicios else 0
    barrera_correcta = min_inicio_fase2 >= max_fin_fase1 - 0.05

    done_fn({
        "n_hilos": n_hilos,
        "duracion_segundos": duracion,
        "barrera_correcta": barrera_correcta,
        "max_fin_fase1": round(max_fin_fase1 % 1000, 4),
        "min_inicio_fase2": round(min_inicio_fase2 % 1000, 4),
        "conclusion": (
            "✅ Barrera correcta. Ningún hilo inició Fase 2 antes de que todos terminaran Fase 1."
            if barrera_correcta else
            "❌ Error en barrera. Algún hilo inició Fase 2 prematuramente."
        ),
    })