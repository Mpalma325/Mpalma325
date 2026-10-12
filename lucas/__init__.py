"""Lucas Claras: generador del sitio de indicadores y calculadoras financieras para Chile.

Módulos principales:

- ``fuentes``: descarga los datos (UF, dólar, euro, UTM, IPC) desde APIs públicas.
- ``datos``: carga los datos descargados y calcula valores derivados (UF futura).
- ``calculos``: fórmulas de sueldo líquido, impuesto único, honorarios, etc.
- ``feriados``: feriados legales de Chile calculados a partir de la ley.
- ``construir``: genera el sitio estático completo en ``dist/``.
"""

__version__ = "1.0.0"
