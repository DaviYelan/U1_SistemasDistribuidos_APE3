import threading
import time
import random

class MiSemaforo:
    def __init__(self, valor):
        self.contador = valor
        self.cerrojo = threading.Lock()
        self.cola_espera = threading.Condition(self.cerrojo)

    def esperar(self):
        with self.cola_espera:
            while self.contador == 0:
                self.cola_espera.wait()
            self.contador -= 1

    def senial(self):
        with self.cola_espera:
            self.contador += 1
            self.cola_espera.notify()

def run_gimnasio_simulation(n_maquinas=3, n_atletas=8, tiempo_max_uso=2):
    semaforo = MiSemaforo(n_maquinas)
    logs = []
    logs_lock = threading.Lock()
    max_simultaneos = [0]
    usando_ahora = [0]
    contador_lock = threading.Lock()

    def atleta(atleta_id):
        tiempo_espera_inicio = time.time()
        logs_lock.acquire()
        logs.append({
            "atleta": atleta_id,
            "evento": "⏳ Esperando máquina",
            "semaforo_valor": semaforo.contador,
            "timestamp": round(time.time() % 100, 3)
        })
        logs_lock.release()

        semaforo.esperar()  # Intento de adquirir máquina

        espera = round(time.time() - tiempo_espera_inicio, 3)

        with contador_lock:
            usando_ahora[0] += 1
            if usando_ahora[0] > max_simultaneos[0]:
                max_simultaneos[0] = usando_ahora[0]

        with logs_lock:
            logs.append({
                "atleta": atleta_id,
                "evento": "💪 Usando máquina",
                "semaforo_valor": semaforo.contador,
                "tiempo_espera": espera,
                "usando_simultaneamente": usando_ahora[0],
                "timestamp": round(time.time() % 100, 3)
            })

        # Sección crítica: usar la máquina
        tiempo_uso = random.uniform(0.2, tiempo_max_uso)
        time.sleep(tiempo_uso)

        with contador_lock:
            usando_ahora[0] -= 1

        semaforo.senial()  # Liberar máquina

        with logs_lock:
            logs.append({
                "atleta": atleta_id,
                "evento": "✅ Terminó, máquina liberada",
                "semaforo_valor": semaforo.contador,
                "tiempo_uso": round(tiempo_uso, 3),
                "timestamp": round(time.time() % 100, 3)
            })

    hilos = []
    inicio = time.time()
    for i in range(n_atletas):
        t = threading.Thread(target=atleta, args=(i + 1,))
        hilos.append(t)
        t.start()
        time.sleep(0.05)  # Pequeño delay para escalonar llegadas

    for t in hilos:
        t.join()

    duracion = round(time.time() - inicio, 3)
    max_real = max_simultaneos[0]
    correcto = max_real <= n_maquinas

    return {
        "n_maquinas": n_maquinas,
        "n_atletas": n_atletas,
        "max_simultaneos_registrado": max_real,
        "limite_correcto": correcto,
        "duracion_segundos": duracion,
        "logs": logs,
        "conclusion": (
            f"✅ Semáforo correcto. Máximo simultáneo={max_real} ≤ {n_maquinas} máquinas"
            if correcto else
            f"❌ Error. Máximo={max_real} superó el límite de {n_maquinas}"
        )
    }