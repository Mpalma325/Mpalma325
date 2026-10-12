# Datos

GitHub Actions descarga aquí los indicadores (UF, dólar, euro, UTM e IPC) y los
sube al repositorio en cada actualización. Así el sitio siempre tiene un respaldo
aunque la API de origen se caiga.

- `series/<indicador>.json`: `{"AAAA-MM-DD": valor}`. La UTM y el IPC usan el
  primer día del mes. El IPC es la variación mensual en % (0.4 = 0,4%).
- `ultimos.json`: último valor de otros indicadores (TPM, cobre, IMACEC...).
- `meta.json`: fecha de la última actualización.

No edites estos archivos a mano: se regeneran solos con `python -m lucas actualizar`.
