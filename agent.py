from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

from config import obtener_modelo
from tools import herramientas

MENSAJE_SISTEMA = SystemMessage(
    content=(
        "Sos un asistente util y conciso. Responde siempre en texto plano y natural, "
        "sin usar asteriscos, sin listas con asteriscos (*) y sin negritas de markdown (**). "
        "Escribe la respuesta en oraciones directas y normales, como una persona real."
    )
)


class EstadoAgente(MessagesState):
    """Estado del agente que hereda de MessagesState para gestionar el historial de mensajes."""
    pass


def crear_grafo_agente():
    """Construye y configura el StateGraph con el nodo del modelo, herramientas y aristas condicionales."""
    modelo = obtener_modelo()
    modelo_con_herramientas = modelo.bind_tools(herramientas)

    async def nodo_modelo(estado: EstadoAgente) -> dict:
        mensajes = estado["messages"]
        if not any(getattr(m, "type", "") == "system" for m in mensajes):
            mensajes = [MENSAJE_SISTEMA] + list(mensajes)
        respuesta = await modelo_con_herramientas.ainvoke(mensajes)
        return {"messages": [respuesta]}

    nodo_herramientas = ToolNode(herramientas)

    grafo = StateGraph(EstadoAgente)
    grafo.add_node("modelo", nodo_modelo)
    grafo.add_node("tools", nodo_herramientas)

    grafo.add_edge(START, "modelo")
    grafo.add_conditional_edges("modelo", tools_condition)
    grafo.add_edge("tools", "modelo")

    return grafo
