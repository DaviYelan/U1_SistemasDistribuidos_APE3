import threading
import time
import random


def run_lectores_escritores_simulation(emit_fn, done_fn,
                                       n_lectores=5, n_escritores=2, iteraciones=3):
    cant_lectores = [0]
    mutex_lectores = threading.Lock()
    sem_escritor = threading.Semaphore(1)

    tablon = ["Nota inicial del sistema"]
    lecturas_ok = [0]
    escrituras_ok = [0]

    def lector(lector_id):
        for _ in range(iteraciones):
            time.sleep(random.uniform(1.5, 2.0))

            with mutex_lectores:
                cant_lectores[0] += 1
                if cant_lectores[0] == 1:
                    sem_escritor.acquire()

            emit_fn({
                "actor": f"📖 Estudiante {lector_id}",
                "accion": "INICIO LECTURA",
                "lectores_activos": cant_lectores[0],
                "contenido_tablon": list(tablon[-3:]),
                "timestamp": round(time.time() % 1000, 4),
            })

            contenido_leido = list(tablon)
            lecturas_ok[0] += 1
            time.sleep(random.uniform(1.5, 2.0))

            emit_fn({
                "actor": f"📖 Estudiante {lector_id}",
                "accion": "FIN LECTURA",
                "lectores_activos": cant_lectores[0],
                "leido": contenido_leido[-1] if contenido_leido else "vacío",
                "timestamp": round(time.time() % 1000, 4),
            })

            with mutex_lectores:
                cant_lectores[0] -= 1
                if cant_lectores[0] == 0:
                    sem_escritor.release()

    notas = [
        "📝 Examen parcial: Viernes 10am",
        "📝 Tarea de Redes entregada",
        "📝 Laboratorio cancelado",
        "📝 Nueva calificación publicada",
        "📝 Reunión de grupo: Lunes",
    ]

    def escritor(escritor_id):
        for i in range(iteraciones):
            time.sleep(random.uniform(1.5, 2.0))

            emit_fn({
                "actor": f"✏️ Profesor {escritor_id}",
                "accion": "ESPERANDO acceso exclusivo...",
                "lectores_activos": cant_lectores[0],
                "timestamp": round(time.time() % 1000, 4),
            })

            sem_escritor.acquire()

            nota_nueva = random.choice(notas)
            tablon.append(nota_nueva)
            escrituras_ok[0] += 1

            emit_fn({
                "actor": f"✏️ Profesor {escritor_id}",
                "accion": f"ESCRIBE: {nota_nueva}",
                "lectores_activos": cant_lectores[0],
                "tablon_actual": list(tablon[-3:]),
                "timestamp": round(time.time() % 1000, 4),
            })

            time.sleep(random.uniform(1.5, 2.0))
            sem_escritor.release()

            emit_fn({
                "actor": f"✏️ Escritor {escritor_id}",
                "accion": "FIN ESCRITURA - liberó acceso",
                "timestamp": round(time.time() % 1000, 4),
            })

    inicio = time.time()
    hilos = (
        [threading.Thread(target=lector,   args=(i + 1,)) for i in range(n_lectores)] +
        [threading.Thread(target=escritor, args=(i + 1,)) for i in range(n_escritores)]
    )
    random.shuffle(hilos)
    for t in hilos:
        t.start()
    for t in hilos:
        t.join()

    duracion = round(time.time() - inicio, 3)

    done_fn({
        "n_lectores": n_lectores,
        "n_escritores": n_escritores,
        "iteraciones": iteraciones,
        "total_lecturas": lecturas_ok[0],
        "total_escrituras": escrituras_ok[0],
        "tablon_final": tablon,
        "duracion_segundos": duracion,
        "conclusion": (
            f"✅ Patrón Lect-Escr correcto. {lecturas_ok[0]} lecturas concurrentes, "
            f"{escrituras_ok[0]} escrituras exclusivas."
        ),
    })