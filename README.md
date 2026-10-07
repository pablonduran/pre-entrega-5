# Pre-entrega 5 — Agente de Razonamiento Cíclico con Memoria Persistente

Agente conversacional autónomo construido con LangGraph, ciclo ReAct con herramientas personalizadas y persistencia de memoria mediante `SqliteSaver`.

## Requisitos

- Python 3.12 o superior
- Clave de API de Google Gemini, OpenAI o Anthropic

## Instalación

1. Crear y activar entorno virtual:
```bash
python -m venv .venv
# En Windows:
.venv\Scripts\Activate.ps1
# En Linux / Mac:
# source .venv/bin/activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
Crear archivo `.env` a partir de `.env.example`:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=tu_clave_de_gemini
# O para OpenAI:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=tu_clave_de_openai
```

## Ejecución

Ejecutar la prueba con razonamiento multi-paso y validación de memoria persistente:
```bash
python main.py
```

La ejecución guarda automáticamente el historial estructurado en `traza_ejecucion.json`.

## Ejemplo de la traza de ejecución

### Turno 1: Razonamiento multi-paso (invocación de 2 herramientas)
- Usuario: "Consultame los datos del cliente con email ana.gomez@hotmail.com y decime cuantos pedidos tiene y el monto de su ultimo pedido."
- Invocacion 1: El modelo llama a buscar_cliente(identificador="ana.gomez@hotmail.com") y obtiene id_cliente 102.
- Invocacion 2: El modelo llama a buscar_pedidos_cliente(id_cliente=102) y recibe la lista de pedidos.
- Respuesta del agente: Ana Gomez se encuentra registrada con el estado activo. Tiene un total de 3 pedidos realizados, y el monto de su ultimo pedido es de 7000.

### Turno 2: Validación de persistencia (mismo thread_id)
- Usuario: "¿Y que producto o servicio especifico adquirio en ese ultimo pedido?"
- Respuesta del agente: En su ultimo pedido, Ana Gomez adquirio el Plan de soporte premium.
(El agente responde directamente utilizando la memoria persistida en SQLite sin tener que volver a consultar los datos del cliente).
