import threading
import time
import random

class BarreraSincronizacion:
    def __init__(self, n_total):
        self.n_total = n_total
        self.contador = 0
        self.mtx_barrera = threading.Lock()
        self.var_cond = threading.Condition(self.mtx_barrera)

    def llegar(self, hilo_id, logs, logs_lock):
        with self.var_cond:
            self.contador += 1
            llegada = self.contador

            with logs_lock:
                logs.append({
                    "hilo": hilo_id,
                    "evento": f"🚩 Llegó a la barrera ({llegada}/{self.n_total})",
                    "fase": "BARRERA",
                    "timestamp": round(time.time() % 1000, 4)
                })

            if self.contador == self.n_total:
                # Último hilo: despierta a todos (broadcast)
                with logs_lock:
                    logs.append({
                        "hilo": hilo_id,
                        "evento": "🔔 ¡ÚLTIMO EN LLEGAR! Despertando a todos...",
                        "fase": "BROADCAST",
                        "timestamp": round(time.time() % 1000, 4)
                    })
                self.var_cond.notify_all()
            else:
                # Los demás esperan (se duerme y suelta el mutex)
                while self.contador < self.n_total:
                    self.var_cond.wait()


def run_barrera_simulation(n_hilos=5):
    barrera = BarreraSincronizacion(n_hilos)
    logs = []
    logs_lock = threading.Lock()

    fase1_tiempos = {}
    fase2_inicios = {}

    def proceso(hilo_id):
        # FASE 1: Trabajo previo (duración variable para simular hilos rápidos/lentos)
        duracion_fase1 = random.uniform(0.2, 1.5)

        with logs_lock:
            logs.append({
                "hilo": hilo_id,
                "evento": f"▶️ Inicia Fase 1 (durará {duracion_fase1:.2f}s)",
                "fase": "FASE_1",
                "timestamp": round(time.time() % 1000, 4)
            })

        time.sleep(duracion_fase1)
        fase1_tiempos[hilo_id] = time.time()

        with logs_lock:
            logs.append({
                "hilo": hilo_id,
                "evento": f"✅ Completó Fase 1 en {duracion_fase1:.2f}s",
                "fase": "FASE_1_FIN",
                "timestamp": round(time.time() % 1000, 4)
            })

        # BARRERA: esperar a todos
        barrera.llegar(hilo_id, logs, logs_lock)

        # FASE 2: Solo comienza cuando TODOS pasaron la barrera
        fase2_inicios[hilo_id] = time.time()

        with logs_lock:
            logs.append({
                "hilo": hilo_id,
                "evento": "🚀 Inicia Fase 2",
                "fase": "FASE_2",
                "timestamp": round(time.time() % 1000, 4)
            })

        time.sleep(random.uniform(0.1, 0.4))

        with logs_lock:
            logs.append({
                "hilo": hilo_id,
                "evento": "🏁 Completó Fase 2",
                "fase": "FASE_2_FIN",
                "timestamp": round(time.time() % 1000, 4)
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

    # Verificar que ningún hilo inició fase 2 antes de que todos terminaran fase 1
    max_fin_fase1 = max(fase1_tiempos.values()) if fase1_tiempos else 0
    min_inicio_fase2 = min(fase2_inicios.values()) if fase2_inicios else 0
    barrera_correcta = min_inicio_fase2 >= max_fin_fase1 - 0.05  # margen pequeño

    logs_sorted = sorted(logs, key=lambda x: x["timestamp"])

    return {
        "n_hilos": n_hilos,
        "duracion_segundos": duracion,
        "barrera_correcta": barrera_correcta,
        "max_fin_fase1": round(max_fin_fase1 % 1000, 4),
        "min_inicio_fase2": round(min_inicio_fase2 % 1000, 4),
        "logs": logs_sorted,
        "conclusion": (
            f"✅ Barrera correcta. Ningún hilo inició Fase 2 antes de que todos terminaran Fase 1."
            if barrera_correcta else
            f"❌ Error en barrera. Algún hilo inició Fase 2 prematuramente."
        )
    }