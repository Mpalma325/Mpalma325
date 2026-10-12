/*
 * Widget de indicadores de Saca la Cuenta (https://sacalacuenta.cl/widget/). ES5, sin dependencias
 * y solo ASCII. Lee api/v1/indicadores.json del mismo origen; si falla, deja el enlace original.
 */
(function () {
  'use strict';

  var MESES = 'enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre'.split(' ');
  var NOMBRES = { uf: 'UF', dolar: 'D\u00f3lar observado', euro: 'Euro', utm: 'UTM' };
  var OSCURO = '--f:#151d20;--x:#e6ecee;--s:#a3b1b8;--b:#2a363b;--p:#2fbfb1';
  // Valen en el Shadow DOM y en el respaldo sin el (prefijo lcw).
  var CSS = '.lcw{all:initial;display:block;max-width:380px;padding:12px 16px;border:1px solid var(--b);' +
    'border-radius:12px;background:var(--f);color:var(--x);text-align:left;font:14px/1.45 system-ui,' +
    'sans-serif;--f:#fff;--x:#1c2427;--s:#55626a;--b:#dde3e6;--p:#0f766e}' +
    '.lcw-oscuro{' + OSCURO + '}@media (prefers-color-scheme:dark){.lcw-auto{' + OSCURO + '}}' +
    '.lcw,.lcw *{box-sizing:border-box}.lcw *{margin:0;padding:0;border:0;font:inherit;color:inherit}' +
    '.lcw .lcw-t{font-weight:700;color:var(--p);padding-bottom:4px}' +
    '.lcw .lcw-f{display:flex;justify-content:space-between;align-items:baseline;padding:6px 0}' +
    '.lcw .lcw-f,.lcw .lcw-pie{border-top:1px solid var(--b)}' +
    '.lcw small{display:block;font-size:12px;color:var(--s)}' +
    '.lcw b{font-size:16px;font-weight:700;font-variant-numeric:tabular-nums;white-space:nowrap;padding-left:12px}' +
    '.lcw .lcw-pie{padding-top:8px;font-size:12px}' +
    '.lcw-pie a{color:var(--p)!important}.lcw-pie ::slotted(a){color:var(--p)!important}';
  var script = document.currentScript;
  var DATOS = (script ? script.src.split('?')[0].replace(/[^\/]*$/, '') : 'https://sacalacuenta.cl/') +
    'api/v1/indicadores.json';
  var datos;
  var esperando;

  function pesos(valor, decimales) { // 38615.3 -> "$38.615,30"
    var f = Math.pow(10, decimales);
    var partes = (Math.floor(valor * f + 0.5) / f).toFixed(decimales).split('.');
    return '$' + partes[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.') + (decimales ? ',' + partes[1] : '');
  }

  function fecha(iso) { // "2026-10-12" -> "12 de octubre"; "2026-10" -> "octubre 2026"
    var p = String(iso).split('-');
    return p[2] ? +p[2] + ' de ' + MESES[p[1] - 1] : MESES[p[1] - 1] + ' ' + p[0];
  }

  function hoyChile() { // AAAA-MM-DD (formato de sv-SE); si falla, queda la UF de hoy
    try {
      return new Intl.DateTimeFormat('sv-SE', { timeZone: 'America/Santiago' }).format(new Date());
    } catch (e) {
      return '';
    }
  }

  function filas(el, d) {
    var pedidos = (el.getAttribute('data-indicadores') || 'uf,dolar,utm').toLowerCase().split(',');
    var html = '';
    for (var i = 0; i < pedidos.length; i++) {
      var clave = pedidos[i].replace(/\s+/g, '');
      var x = NOMBRES[clave] && d[clave];
      if (x && typeof x.valor === 'number') {
        // Pasada la medianoche rige la UF de manana (datos generados 2 veces al dia).
        if (clave === 'uf' && x.manana && x.manana.fecha === hoyChile()) {
          x = x.manana;
        }
        html += '<div class="lcw-f"><span>' + NOMBRES[clave] + '<small>' + fecha(x.fecha || x.mes) +
          '</small></span><b>' + pesos(x.valor, clave === 'utm' ? 0 : 2) + '</b></div>';
      }
    }
    return html;
  }

  function pintar(el, d) {
    var html = filas(el, d);
    var tema = el.getAttribute('data-tema');
    var tarjeta = document.createElement('div');
    var sombra;
    if (!html) {
      return;
    }
    tarjeta.className = 'lcw lcw-' + (tema === 'claro' || tema === 'oscuro' ? tema : 'auto');
    tarjeta.innerHTML = '<div class="lcw-t">Indicadores econ\u00f3micos</div>' + html + '<div class="lcw-pie"></div>';
    try {
      sombra = el.attachShadow({ mode: 'open' });
    } catch (e) {
      // sin Shadow DOM: respaldo con estilos prefijados
    }
    if (sombra) { // el enlace original sigue en la pagina y se ve al pie con <slot>
      sombra.innerHTML = '<style>' + CSS + '</style>';
      tarjeta.lastChild.appendChild(document.createElement('slot'));
      return sombra.appendChild(tarjeta);
    }
    if (!document.getElementById('lcw-css')) {
      var estilos = document.createElement('style');
      estilos.id = 'lcw-css';
      estilos.appendChild(document.createTextNode(CSS));
      document.head.appendChild(estilos);
    }
    while (el.firstChild) {
      tarjeta.lastChild.appendChild(el.firstChild);
    }
    el.appendChild(tarjeta);
  }

  function cargar(listo) {
    if (datos || esperando) {
      return datos ? listo(datos) : esperando.push(listo);
    }
    esperando = [listo];
    var xhr = new XMLHttpRequest();
    xhr.open('GET', DATOS);
    xhr.onload = function () {
      var lista = esperando;
      esperando = null;
      try {
        var d = xhr.status === 200 && JSON.parse(xhr.responseText);
        for (var i = 0; d && d.uf && i < lista.length; i++) {
          datos = d;
          lista[i](d);
        }
      } catch (e) {
        // respuesta inesperada: queda el contenido original
      }
    };
    xhr.onerror = function () {
      esperando = null;
    };
    xhr.send();
  }

  function iniciar() { // muestra los widgets nuevos; se puede volver a llamar
    var lista = document.querySelectorAll('.saca-la-cuenta-widget');
    var nuevos = [];
    for (var i = 0; i < lista.length; i++) {
      if (!lista[i].getAttribute('data-lcw')) {
        lista[i].setAttribute('data-lcw', '1');
        nuevos.push(lista[i]);
      }
    }
    if (nuevos.length) {
      cargar(function (d) {
        for (var j = 0; j < nuevos.length; j++) {
          try {
            pintar(nuevos[j], d);
          } catch (e) {
            // queda el enlace original de ese widget
          }
        }
      });
    }
  }

  window.SacaLaCuentaWidget = { iniciar: iniciar };
  iniciar();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  }
})();
