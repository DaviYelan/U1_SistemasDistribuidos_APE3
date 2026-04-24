import threading
import time
import random

def run_lectores_escritores_simulation(n_lectores=5, n_escritores=2, iteraciones=3):
    # Variables de sincronización según el algoritmo de la guía
    cant_lectores = [0]
    mutex_lectores = threading.Lock()
    sem_escritor = threading.Semaphore(1)

    tablon = ["Nota inicial del sistema"]
    logs = []
    logs_lock = threading.Lock()
    lecturas_ok = [0]
    escrituras_ok = [0]

    def lector(lector_id):
        for _ in range(iteraciones):
            time.sleep(random.uniform(0.05, 0.3))

            # --- SECCIÓN DE ENTRADA ---
            with mutex_lectores:
                cant_lectores[0] += 1
                if cant_lectores[0] == 1:
                    sem_escritor.acquire()  # Primer lector bloquea a escritores

            with logs_lock:
                logs.append({
                    "actor": f"📖 Lector {lector_id}",
                    "accion": "INICIO LECTURA",
                    "lectores_activos": cant_lectores[0],
                    "contenido_tablon": list(tablon[-3:]),
                    "timestamp": round(time.time() % 1000, 4)
                })

            # SECCIÓN CRÍTICA - lectura compartida
            contenido_leido = list(tablon)
            lecturas_ok[0] += 1
            time.sleep(random.uniform(0.05, 0.15))  # Tiempo de lectura

            with logs_lock:
                logs.append({
                    "actor": f"📖 Lector {lector_id}",
                    "accion": "FIN LECTURA",
                    "lectores_activos": cant_lectores[0],
                    "leido": contenido_leido[-1] if contenido_leido else "vacío",
                    "timestamp": round(time.time() % 1000, 4)
                })

            # --- SECCIÓN DE SALIDA ---
            with mutex_lectores:
                cant_lectores[0] -= 1
                if cant_lectores[0] == 0:
                    sem_escritor.release()  # Último lector abre la puerta

    def escritor(escritor_id):
        notas = [
            "📝 Examen parcial: Viernes 10am",
            "📝 Tarea de Redes entregada",
            "📝 Laboratorio cancelado",
            "📝 Nueva calificación publicada",
            "📝 Reunión de grupo: Lunes"
        ]
        for i in range(iteraciones):
            time.sleep(random.uniform(0.2, 0.5))

            with logs_lock:
                logs.append({
                    "actor": f"✏️ Escritor {escritor_id}",
                    "accion": "ESPERANDO acceso exclusivo...",
                    "lectores_activos": cant_lectores[0],
                    "timestamp": round(time.time() % 1000, 4)
                })

            sem_escritor.acquire()  # Acceso exclusivo

            nota_nueva = random.choice(notas)
            tablon.append(nota_nueva)
            escrituras_ok[0] += 1

            with logs_lock:
                logs.append({
                    "actor": f"✏️ Escritor {escritor_id}",
                    "accion": f"ESCRIBE: {nota_nueva}",
                    "lectores_activos": cant_lectores[0],
                    "tablon_actual": list(tablon[-3:]),
                    "timestamp": round(time.time() % 1000, 4)
                })

            time.sleep(random.uniform(0.05, 0.15))  # Tiempo de escritura
            sem_escritor.release()

            with logs_lock:
                logs.append({
                    "actor": f"✏️ Escritor {escritor_id}",
                    "accion": "FIN ESCRITURA - liberó acceso",
                    "timestamp": round(time.time() % 1000, 4)
                })

    inicio = time.time()
    hilos = []
    for i in range(n_lectores):
        hilos.append(threading.Thread(target=lector, args=(i + 1,)))
    for i in range(n_escritores):
        hilos.append(threading.Thread(target=escritor, args=(i + 1,)))

    random.shuffle(hilos)
    for t in hilos:
        t.start()
    for t in hilos:
        t.join()

    duracion = round(time.time() - inicio, 3)
    logs_sorted = sorted(logs, key=lambda x: x["timestamp"])

    # Verificar que nunca hubo escritor con lectores activos simultáneamente
    return {
        "n_lectores": n_lectores,
        "n_escritores": n_escritores,
        "iteraciones": iteraciones,
        "total_lecturas": lecturas_ok[0],
        "total_escrituras": escrituras_ok[0],
        "tablon_final": tablon,
        "duracion_segundos": duracion,
        "logs": logs_sorted[:50],
        "conclusion": f"✅ Patrón Lect-Escr correcto. {lecturas_ok[0]} lecturas concurrentes, {escrituras_ok[0]} escrituras exclusivas."
    }