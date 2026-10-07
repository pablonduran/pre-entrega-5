import asyncio
import json
from pathlib import Path
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from agent import crear_grafo_agente

RUTA_BD_PERSISTENCIA = "checkpoints.db"
RUTA_TRAZA_JSON = Path("traza_ejecucion.json")


def formatear_contenido(contenido) -> str:
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        textos = []
        for elemento in contenido:
            if isinstance(elemento, dict) and "text" in elemento:
                textos.append(elemento["text"])
            else:
                textos.append(str(elemento))
        return " ".join(textos)
    return str(contenido)


def mensaje_a_dict(mensaje) -> dict:
    datos = {
        "rol": mensaje.type,
        "contenido": formatear_contenido(mensaje.content),
    }
    if hasattr(mensaje, "tool_calls") and mensaje.tool_calls:
        datos["llamadas_herramientas"] = mensaje.tool_calls
    if hasattr(mensaje, "name") and mensaje.name:
        datos["nombre_herramienta"] = mensaje.name
    return datos


async def ejecutar_agente():
    grafo = crear_grafo_agente()
    traza_completa = []

    async with AsyncSqliteSaver.from_conn_string(RUTA_BD_PERSISTENCIA) as memoria_persistencia:
        agente = grafo.compile(checkpointer=memoria_persistencia)

        # Configuracion con identificador de sesion y limite de recursion
        configuracion_sesion = {
            "configurable": {"thread_id": "sesion-cliente-102"},
            "recursion_limit": 10,
        }

        # -------------------------------------------------------------
        # Turno 1: Razonamiento multi-paso (invocacion de >= 2 herramientas)
        # -------------------------------------------------------------
        pregunta_1 = (
            "Consultame los datos del cliente con email ana.gomez@hotmail.com y "
            "decime cuantos pedidos tiene y el monto de su ultimo pedido."
        )

        print("\nTurno 1: Razonamiento multi-paso")
        print(f"Usuario: {pregunta_1}\n")

        estado_turno_1 = await agente.ainvoke(
            {"messages": [HumanMessage(content=pregunta_1)]},
            configuracion_sesion,
        )

        mensajes_turno_1 = estado_turno_1["messages"]
        for m in mensajes_turno_1:
            if getattr(m, "tool_calls", None):
                print(f"-> [Accion LLM]: Invoca herramienta {m.tool_calls}")
            elif m.type == "tool":
                print(f"-> [Respuesta Herramienta]: {m.content}")

        respuesta_final_1 = formatear_contenido(mensajes_turno_1[-1].content)
        print(f"\nRespuesta Agente:\n{respuesta_final_1}")

        traza_completa.append({
            "turno": 1,
            "tipo_prueba": "Razonamiento multi-paso (>= 2 herramientas)",
            "mensajes": [mensaje_a_dict(m) for m in mensajes_turno_1],
        })

        # -------------------------------------------------------------
        # Turno 2: Persistencia de memoria en el mismo thread_id
        # -------------------------------------------------------------
        pregunta_2 = "¿Y que producto o servicio especifico adquirio en ese ultimo pedido?"

        print("\nTurno 2: Validacion de memoria persistente (mismo thread_id)")
        print(f"Usuario: {pregunta_2}\n")

        estado_turno_2 = await agente.ainvoke(
            {"messages": [HumanMessage(content=pregunta_2)]},
            configuracion_sesion,
        )

        mensajes_nuevos_turno_2 = estado_turno_2["messages"][len(mensajes_turno_1):]
        for m in mensajes_nuevos_turno_2:
            if getattr(m, "tool_calls", None):
                print(f"-> [Accion LLM]: Invoca herramienta {m.tool_calls}")
            elif m.type == "tool":
                print(f"-> [Respuesta Herramienta]: {m.content}")

        respuesta_final_2 = formatear_contenido(estado_turno_2["messages"][-1].content)
        print(f"\nRespuesta Agente:\n{respuesta_final_2}")

        traza_completa.append({
            "turno": 2,
            "tipo_prueba": "Memoria persistente (contexto recordado sin reiniciar)",
            "mensajes": [mensaje_a_dict(m) for m in mensajes_nuevos_turno_2],
        })

    # Guardado de la traza de ejecucion en archivo JSON
    with open(RUTA_TRAZA_JSON, "w", encoding="utf-8") as f:
        json.dump(traza_completa, f, indent=2, ensure_ascii=False)
    print(f"\n[INFO] Traza de ejecucion guardada en '{RUTA_TRAZA_JSON}'.")


if __name__ == "__main__":
    asyncio.run(ejecutar_agente())
