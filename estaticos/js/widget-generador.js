/*
 * Generador del código del widget (página /widget/): arma el código para insertar con los
 * indicadores y el tema elegidos, actualiza la vista previa y copia el código.
 * El widget en sí está en widget/widget.js y se publica en /widget.js.
 */
(function () {
  'use strict';

  /** Igual que html.escape de Python, para que el código coincida con lucas/api.py. */
  function escapar(texto) {
    return String(texto).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#x27;');
  }

  function copiar(codigo, estado) {
    var listo = function () {
      estado.textContent = 'Código copiado. Pégalo en tu sitio donde quieras mostrar el widget.';
    };
    var manual = function () {
      codigo.focus();
      codigo.select();
      var copiado = false;
      try {
        copiado = document.execCommand('copy');
      } catch (error) {
        copiado = false;
      }
      if (copiado) {
        listo();
      } else {
        estado.textContent = 'Selecciona el código y cópialo con Ctrl+C (o Cmd+C en Mac).';
      }
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(codigo.value).then(listo, manual);
    } else {
      manual();
    }
  }

  function iniciar() {
    var form = document.getElementById('generador-widget');
    var codigo = document.getElementById('codigo-widget');
    var vista = document.getElementById('vista-previa-widget');
    var boton = document.getElementById('copiar-widget');
    var estado = document.getElementById('copiar-estado');
    if (!form || !codigo || !vista || !estado) {
      return;
    }
    var url = form.getAttribute('data-url');
    var texto = form.getAttribute('data-texto');
    var casillas = Array.prototype.slice.call(form.querySelectorAll('input[name="indicador"]'));

    function elegidos() {
      return casillas.filter(function (c) { return c.checked; }).map(function (c) { return c.value; });
    }

    function bloque(indicadores, tema, destino, rel) {
      return '<div class="lucas-claras-widget" data-indicadores="' + indicadores.join(',') +
        '" data-tema="' + tema + '"><a href="' + escapar(destino) + '"' + rel + '>' + escapar(texto) + '</a></div>';
    }

    function actualizar() {
      var indicadores = elegidos();
      var marcado = form.querySelector('input[name="tema"]:checked');
      var tema = marcado ? marcado.value : 'auto';
      codigo.value = bloque(indicadores, tema, url + '/', ' rel="nofollow"') +
        '\n<script async src="' + escapar(url) + '/widget.js"></script>';
      estado.textContent = '';
      // Vista previa: un elemento nuevo, porque el Shadow DOM de un elemento no se puede reemplazar.
      vista.innerHTML = bloque(indicadores, tema, form.getAttribute('data-inicio'), '');
      if (window.LucasClarasWidget) {
        window.LucasClarasWidget.iniciar();
      }
    }

    form.addEventListener('change', function (evento) {
      // Siempre al menos un indicador.
      if (evento.target.name === 'indicador' && !elegidos().length) {
        evento.target.checked = true;
      }
      actualizar();
    });
    codigo.addEventListener('focus', function () { codigo.select(); });
    if (boton) {
      boton.addEventListener('click', function () { copiar(codigo, estado); });
    }
    // Por si el navegador recordó opciones de una visita anterior.
    actualizar();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();
