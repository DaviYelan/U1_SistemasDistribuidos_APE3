import threading
import time


def run_mutex_simulation(emit_fn, done_fn, n_hilos=5, m_ventas=200, usar_mutex=True):
    boletos_vendidos = 0
    lock = threading.Lock()

    def ejecutar_venta_con_mutex(hilo_id):
        nonlocal boletos_vendidos
        for i in range(m_ventas):
            with lock:
                time.sleep(0.005)  # pausa entre cada venta
                boletos_vendidos += 1
                valor_despues = boletos_vendidos
            if i % (m_ventas // 5) == 0:
                emit_fn({
                    "hilo": hilo_id,
                    "operacion": i + 1,
                    "valor": valor_despues,
                    "tipo": "mutex",
                })

    def ejecutar_venta_sin_mutex(hilo_id):
        nonlocal boletos_vendidos
        for i in range(m_ventas):
            valor_leido = boletos_vendidos
            time.sleep(0.005)           # forzar cambio de contexto
            boletos_vendidos = valor_leido + 1
            if i % (m_ventas // 5) == 0:
                emit_fn({
                    "hilo": hilo_id,
                    "operacion": i + 1,
                    "valor": boletos_vendidos,
                    "tipo": "sin_mutex",
                })

    hilos = []
    inicio = time.time()
    for j in range(n_hilos):
        target = ejecutar_venta_con_mutex if usar_mutex else ejecutar_venta_sin_mutex
        t = threading.Thread(target=target, args=(j + 1,))
        hilos.append(t)
        t.start()

    for t in hilos:
        t.join()

    duracion = round(time.time() - inicio, 4)
    esperado = n_hilos * m_ventas
    correcto = boletos_vendidos == esperado

    done_fn({
        "resultado_final": boletos_vendidos,
        "esperado": esperado,
        "correcto": correcto,
        "usando_mutex": usar_mutex,
        "n_hilos": n_hilos,
        "m_ventas": m_ventas,
        "duracion_segundos": duracion,
        "conclusion": (
            f"✅ Mutex funcionó correctamente. Total={boletos_vendidos} == Esperado={esperado}"
            if correcto else
            f"⚠️ Condición de carrera detectada. Total={boletos_vendidos} ≠ Esperado={esperado} "
            f"(perdidos={esperado - boletos_vendidos})"
        ),
    })