from langchain_core.tools import tool

# Base de datos simulada en memoria
CLIENTES_DB = {
    "ana.gomez@hotmail.com": {"id_cliente": 102, "nombre": "Ana Gomez", "email": "ana.gomez@hotmail.com", "estado": "activo"},
    "carlos.lopez@hotmail.com": {"id_cliente": 103, "nombre": "Carlos Lopez", "email": "carlos.lopez@hotmail.com", "estado": "activo"},
    "102": {"id_cliente": 102, "nombre": "Ana Gomez", "email": "ana.gomez@hotmail.com", "estado": "activo"},
    "103": {"id_cliente": 103, "nombre": "Carlos Lopez", "email": "carlos.lopez@hotmail.com", "estado": "activo"},
}

PEDIDOS_DB = {
    102: {
        "id_cliente": 102,
        "cantidad_pedidos": 3,
        "total_acumulado": 14500,
        "pedidos": [
            {"id_pedido": 501, "fecha": "2026-08-15", "monto": 3000, "producto": "Licencia software basic"},
            {"id_pedido": 502, "fecha": "2026-09-02", "monto": 4500, "producto": "Servidor cloud adicional"},
            {"id_pedido": 503, "fecha": "2026-10-01", "monto": 7000, "producto": "Plan de soporte premium"},
        ],
    },
    103: {
        "id_cliente": 103,
        "cantidad_pedidos": 1,
        "total_acumulado": 5000,
        "pedidos": [
            {"id_pedido": 601, "fecha": "2026-09-20", "monto": 5000, "producto": "Consultoria tecnica"},
        ],
    },
}


@tool
def buscar_cliente(identificador: str) -> dict:
    """Busca un cliente en el sistema por su direccion de email o por su ID numerico.

    Util para obtener el id_cliente necesario antes de consultar pedidos u operaciones.
    Devuelve los datos del cliente (id_cliente, nombre, email, estado).
    """
    id_limpio = identificador.strip().lower()
    if id_limpio in CLIENTES_DB:
        return CLIENTES_DB[id_limpio]
    return {"error": f"No se encontro ningun cliente con el identificador '{identificador}'."}


@tool
def buscar_pedidos_cliente(id_cliente: int) -> dict:
    """Consulta el historial de pedidos de un cliente mediante su ID numerico (id_cliente).

    Devuelve la cantidad de pedidos, el total acumulado en dinero y la lista detallada de pedidos.
    """
    if id_cliente in PEDIDOS_DB:
        return PEDIDOS_DB[id_cliente]
    return {
        "id_cliente": id_cliente,
        "cantidad_pedidos": 0,
        "total_acumulado": 0,
        "pedidos": [],
        "mensaje": "El cliente no registra pedidos realizados.",
    }


herramientas = [buscar_cliente, buscar_pedidos_cliente]
