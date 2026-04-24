import threading
import time

def run_mutex_simulation(n_hilos=5, m_ventas=200, usar_mutex=True):
    boletos_vendidos = 0
    logs = []
    lock = threading.Lock()
    errores_carrera = []

    def ejecutar_venta_con_mutex(hilo_id):
        nonlocal boletos_vendidos
        for i in range(m_ventas):
            with lock:
                valor_antes = boletos_vendidos
                # Simular pequeño delay de operación - sección crítica
                boletos_vendidos += 1
                valor_despues = boletos_vendidos
            if i % (m_ventas // 5) == 0:
                logs.append({
                    "hilo": hilo_id,
                    "operacion": i + 1,
                    "valor": valor_despues,
                    "tipo": "mutex"
                })

    def ejecutar_venta_sin_mutex(hilo_id):
        nonlocal boletos_vendidos
        for i in range(m_ventas):
            # Sin protección: condición de carrera posible
            valor_leido = boletos_vendidos
            time.sleep(0)  # Forzar cambio de contexto
            boletos_vendidos = valor_leido + 1
            if i % (m_ventas // 5) == 0:
                logs.append({
                    "hilo": hilo_id,
                    "operacion": i + 1,
                    "valor": boletos_vendidos,
                    "tipo": "sin_mutex"
                })

    hilos = []
    inicio = time.time()

    for j in range(n_hilos):
        if usar_mutex:
            t = threading.Thread(target=ejecutar_venta_con_mutex, args=(j + 1,))
        else:
            t = threading.Thread(target=ejecutar_venta_sin_mutex, args=(j + 1,))
        hilos.append(t)
        t.start()

    for t in hilos:
        t.join()

    duracion = round(time.time() - inicio, 4)
    esperado = n_hilos * m_ventas
    correcto = boletos_vendidos == esperado

    return {
        "resultado_final": boletos_vendidos,
        "esperado": esperado,
        "correcto": correcto,
        "usando_mutex": usar_mutex,
        "n_hilos": n_hilos,
        "m_ventas": m_ventas,
        "duracion_segundos": duracion,
        "logs": sorted(logs, key=lambda x: (x["hilo"], x["operacion"]))[:30],
        "conclusion": (
            f"✅ Mutex funcionó correctamente. Total={boletos_vendidos} == Esperado={esperado}"
            if correcto else
            f"⚠️ Condición de carrera detectada. Total={boletos_vendidos} ≠ Esperado={esperado} (perdidos={(esperado - boletos_vendidos)})"
        )
    }