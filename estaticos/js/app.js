/*
 * Interactividad de Lucas Claras: conversores, calculadoras, UF del día y
 * próximo feriado. Sin dependencias. Las fórmulas viven en calculos.js.
 */
(function () {
  'use strict';

  var MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
    'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var DIAS = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];

  // ---------------------------------------------------------------------------
  // Utilidades
  // ---------------------------------------------------------------------------

  function $(selector, contexto) {
    return (contexto || document).querySelector(selector);
  }

  function $$(selector, contexto) {
    return Array.prototype.slice.call((contexto || document).querySelectorAll(selector));
  }

  function leerJSON(id) {
    var elemento = document.getElementById(id);
    if (!elemento) {
      return null;
    }
    try {
      return JSON.parse(elemento.textContent);
    } catch (error) {
      return null;
    }
  }

  function redondear(valor, decimales) {
    var factor = Math.pow(10, decimales || 0);
    return valor < 0 ? -Math.floor(-valor * factor + 0.5) / factor : Math.floor(valor * factor + 0.5) / factor;
  }

  function numero(valor, decimales) {
    decimales = decimales || 0;
    var r = redondear(Math.abs(valor), decimales);
    var partes = r.toFixed(decimales).split('.');
    var entero = partes[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    var signo = valor < 0 && r !== 0 ? '-' : '';
    return signo + entero + (decimales > 0 ? ',' + partes[1] : '');
  }

  function pesos(valor, decimales) {
    var r = redondear(valor, decimales || 0);
    return (r < 0 ? '-$' : '$') + numero(Math.abs(r), decimales || 0);
  }

  function porcentaje(fraccion, decimales, signo) {
    var d = decimales === undefined ? 1 : decimales;
    var v = redondear(fraccion * 100, d);
    var texto = numero(v, d) + '%';
    return signo && v > 0 ? '+' + texto : texto;
  }

  /** Lee "1.000.000", "1000000", "39,5", "4.5" o "$ 1.200" como número. */
  function leerNumero(texto) {
    if (texto === null || texto === undefined) {
      return NaN;
    }
    var t = String(texto).replace(/[\s$%]/g, '').replace(/UF/gi, '');
    if (t === '') {
      return NaN;
    }
    if (t.indexOf(',') !== -1) {
      t = t.replace(/\./g, '').replace(',', '.');
    } else if (/^-?\d{1,3}(\.\d{3})+$/.test(t)) {
      t = t.replace(/\./g, '');
    }
    var n = parseFloat(t);
    return isFinite(n) ? n : NaN;
  }

  function hoyChile() {
    try {
      var partes = new Intl.DateTimeFormat('en-CA', {
        timeZone: 'America/Santiago', year: 'numeric', month: '2-digit', day: '2-digit'
      }).formatToParts(new Date());
      var v = {};
      partes.forEach(function (parte) { v[parte.type] = parte.value; });
      return v.year + '-' + v.month + '-' + v.day;
    } catch (error) {
      var d = new Date();
      return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
    }
  }

  function aFechaUTC(iso) {
    var p = iso.split('-');
    return new Date(Date.UTC(+p[0], +p[1] - 1, +p[2]));
  }

  function fechaLarga(iso, conDia) {
    var p = iso.split('-');
    var texto = (+p[2]) + ' de ' + MESES[+p[1] - 1] + ' de ' + p[0];
    return conDia ? DIAS[aFechaUTC(iso).getUTCDay()] + ' ' + texto : texto;
  }

  function capitalizar(texto) {
    return texto.charAt(0).toUpperCase() + texto.slice(1);
  }

  function datosPagina() {
    return leerJSON('datos-pagina') || {};
  }

  // ---------------------------------------------------------------------------
  // Formularios: lectura, enlaces para compartir y formato de montos
  // ---------------------------------------------------------------------------

  function leerFormulario(form) {
    var datos = {};
    $$('input, select', form).forEach(function (campo) {
      if (!campo.name) {
        return;
      }
      if (campo.type === 'radio') {
        if (campo.checked) {
          datos[campo.name] = campo.value;
        }
      } else if (campo.type === 'checkbox') {
        datos[campo.name] = campo.checked;
      } else {
        datos[campo.name] = campo.value;
      }
    });
    return datos;
  }

  function guardarEnEnlace(form) {
    if (!window.history || !history.replaceState) {
      return;
    }
    var datos = leerFormulario(form);
    var partes = Object.keys(datos).map(function (clave) {
      var valor = datos[clave] === true ? '1' : (datos[clave] === false ? '0' : datos[clave]);
      return encodeURIComponent(clave) + '=' + encodeURIComponent(valor);
    });
    history.replaceState(null, '', '#' + partes.join('&'));
  }

  function cargarDesdeEnlace(form) {
    if (!location.hash || location.hash.length < 2) {
      return;
    }
    location.hash.slice(1).split('&').forEach(function (par) {
      var kv = par.split('=');
      var nombre = decodeURIComponent(kv[0] || '');
      var valor = decodeURIComponent(kv[1] || '');
      $$('input, select', form).forEach(function (campo) {
        if (campo.name !== nombre) {
          return;
        }
        if (campo.type === 'radio') {
          campo.checked = campo.value === valor;
        } else if (campo.type === 'checkbox') {
          campo.checked = valor === '1';
        } else {
          campo.value = valor;
        }
      });
    });
  }

  function iniciarCompartir(contenedor) {
    $$('[data-compartir]', contenedor).forEach(function (boton) {
      var original = boton.textContent;
      boton.addEventListener('click', function () {
        var listo = function () {
          boton.textContent = '¡Enlace copiado!';
          setTimeout(function () { boton.textContent = original; }, 2000);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(location.href).then(listo, function () {
            window.prompt('Copia este enlace:', location.href);
          });
        } else {
          window.prompt('Copia este enlace:', location.href);
        }
      });
    });
  }

  function iniciarMontos(form) {
    $$('input[data-dinero]', form).forEach(function (input) {
      input.addEventListener('blur', function () {
        var n = leerNumero(input.value);
        if (!isNaN(n)) {
          input.value = numero(n, 0);
        }
      });
    });
  }

  /** Conecta un formulario de calculadora con su función de cálculo. */
  function calculadora(form, resultado, calcular) {
    cargarDesdeEnlace(form);
    iniciarMontos(form);
    iniciarCompartir(resultado.parentNode);
    var ejecutar = function () {
      try {
        calcular(form, resultado);
      } catch (error) {
        poner(resultado, 'principal', '—');
      }
    };
    form.addEventListener('input', function () {
      ejecutar();
      guardarEnEnlace(form);
    });
    form.addEventListener('change', function () {
      ejecutar();
      guardarEnEnlace(form);
    });
    ejecutar();
  }

  function poner(contenedor, clave, texto) {
    $$('[data-r="' + clave + '"]', contenedor).forEach(function (el) {
      el.textContent = texto;
    });
  }

  function mostrarFila(contenedor, clave, visible) {
    $$('[data-fila="' + clave + '"]', contenedor).forEach(function (el) {
      el.hidden = !visible;
    });
  }

  function alternar(form, selector, visible) {
    $$(selector, form).forEach(function (el) {
      el.hidden = !visible;
    });
  }

  // ---------------------------------------------------------------------------
  // UF del día (por si la página se generó hace un par de días)
  // ---------------------------------------------------------------------------

  function actualizarUf() {
    var ventana = leerJSON('uf-ventana') || {};
    var hoy = hoyChile();
    var valor = ventana[hoy];
    if (!valor) {
      return;
    }
    $$('[data-uf-hoy]').forEach(function (el) { el.textContent = pesos(valor, 2); });
    $$('[data-uf-fecha]').forEach(function (el) { el.textContent = fechaLarga(hoy, true); });
    $$('[data-uf-monto]').forEach(function (el) {
      el.textContent = pesos(valor * parseFloat(el.getAttribute('data-uf-monto')), 0);
    });
    $$('form[data-es-uf]').forEach(function (form) {
      form.setAttribute('data-tasa', valor);
      recalcularConversor(form, 'origen');
    });
  }

  // ---------------------------------------------------------------------------
  // Conversores (UF, dólar, euro, UTM)
  // ---------------------------------------------------------------------------

  function recalcularConversor(form, desde) {
    var tasa = parseFloat(form.getAttribute('data-tasa'));
    var origen = $('[data-lado="origen"]', form);
    var destino = $('[data-lado="destino"]', form);
    if (desde === 'origen') {
      var a = leerNumero(origen.value);
      var decimales = +form.getAttribute('data-dec-destino');
      if (form.hasAttribute('data-es-uf') && Math.abs(a) < 10) {
        decimales = 2;
      }
      destino.value = isNaN(a) ? '' : numero(a * tasa, decimales);
    } else {
      var b = leerNumero(destino.value);
      origen.value = isNaN(b) ? '' : numero(b / tasa, +form.getAttribute('data-dec-origen'));
    }
  }

  function iniciarConversores() {
    $$('form[data-conversor]').forEach(function (form) {
      $$('input', form).forEach(function (input) {
        input.addEventListener('input', function () {
          recalcularConversor(form, input.getAttribute('data-lado'));
        });
      });
    });
  }

  // ---------------------------------------------------------------------------
  // Calculadoras
  // ---------------------------------------------------------------------------

  var L = window.LucasCalculos;

  function calcSueldo(form, res) {
    var p = datosPagina().parametros;
    var d = leerFormulario(form);
    var modoBruto = d.modo !== 'liquido';
    alternar(form, '[data-solo-isapre]', d.salud === 'isapre');
    alternar(form, '[data-solo-bruto]', modoBruto);
    var etiqueta = $('label[for="s-monto"]', form);
    etiqueta.textContent = etiqueta.getAttribute(modoBruto ? 'data-etiqueta-bruto' : 'data-etiqueta-liquido');
    $('[data-r-etiqueta]', res).textContent = modoBruto ? 'Sueldo líquido' : 'Sueldo bruto necesario';

    var monto = leerNumero(d.monto);
    if (isNaN(monto) || monto <= 0) {
      poner(res, 'principal', '—');
      return;
    }
    var opciones = {
      afp: d.afp,
      salud: d.salud,
      plan_isapre_uf: leerNumero(d.plan) || 0,
      contrato: d.contrato,
      no_imponible: leerNumero(d.no_imponible) || 0,
      apv: leerNumero(d.apv) || 0
    };
    var gratificacion = 0;
    var r;
    if (modoBruto) {
      var bruto = monto;
      if (d.gratificacion) {
        gratificacion = L.gratificacionLegal(monto, p);
        bruto = monto + gratificacion;
      }
      r = L.sueldoLiquido(bruto, p, opciones);
    } else {
      r = L.brutoParaLiquido(monto, p, opciones);
    }
    var costo = L.costoEmpleador(r.bruto, p, opciones.contrato, opciones.no_imponible);

    poner(res, 'principal', pesos(modoBruto ? r.liquido : r.bruto));
    poner(res, 'bruto', pesos(r.bruto));
    poner(res, 'gratificacion', pesos(gratificacion));
    mostrarFila(res, 'gratificacion', gratificacion > 0);
    poner(res, 'no_imponible', pesos(r.no_imponible));
    mostrarFila(res, 'no_imponible', r.no_imponible > 0);
    poner(res, 'tasa_afp', '(' + porcentaje(r.tasa_afp_total, 2) + ')');
    poner(res, 'afp', pesos(-r.afp));
    poner(res, 'salud', pesos(-r.salud));
    poner(res, 'cesantia', pesos(-r.cesantia));
    poner(res, 'apv', pesos(-r.apv));
    mostrarFila(res, 'apv', r.apv > 0);
    poner(res, 'impuesto', pesos(-r.impuesto));
    poner(res, 'liquido', pesos(r.liquido));
    var nota = 'Base tributable: ' + pesos(r.base_tributable) + ' · Tasa marginal de impuesto: ' +
      porcentaje(r.tasa_marginal, 1);
    if (r.tope_aplicado) {
      nota += ' · Se aplicó el tope imponible';
    }
    if (r.salud_adicional > 0) {
      nota += ' · Incluye ' + pesos(r.salud_adicional) + ' de cotización adicional de isapre';
    }
    poner(res, 'nota', nota);
    poner(res, 'costo_total', pesos(costo.costo_total));
    poner(res, 'e_cesantia', pesos(costo.cesantia));
    poner(res, 'e_reforma', pesos(costo.reforma));
    poner(res, 'e_sis', pesos(costo.sis));
    poner(res, 'e_mutual', pesos(costo.mutual));
  }

  function calcHonorarios(form, res) {
    var p = datosPagina().parametros;
    var d = leerFormulario(form);
    var monto = leerNumero(d.monto);
    if (isNaN(monto) || monto <= 0) {
      return;
    }
    var r = d.modo === 'liquido' ? L.honorariosDesdeLiquido(monto, p) : L.honorariosDesdeBruto(monto, p);
    poner(res, 'bruto', pesos(r.bruto));
    poner(res, 'retencion', pesos(-r.retencion));
    poner(res, 'liquido', pesos(r.liquido));
  }

  function calcArriendo(form, res) {
    var ipc = datosPagina().ipc || {};
    var meses = Object.keys(ipc).sort();
    var d = leerFormulario(form);
    var monto = leerNumero(d.monto);
    var desde = d.desde;
    var hasta = d.hasta;
    if (desde > hasta) {
      var aux = desde;
      desde = hasta;
      hasta = aux;
    }
    var periodo = meses.filter(function (m) { return m >= desde && m <= hasta; });
    if (isNaN(monto) || monto <= 0 || !periodo.length) {
      poner(res, 'nuevo', '—');
      return;
    }
    var r = L.reajustarPorIpc(monto, periodo.map(function (m) { return ipc[m]; }));
    var nombreMes = function (m) {
      var partes = m.split('-');
      return MESES[+partes[1] - 1] + ' ' + partes[0];
    };
    poner(res, 'nuevo', pesos(r.nuevo_monto));
    poner(res, 'variacion', porcentaje(r.variacion, 2, true));
    poner(res, 'diferencia', pesos(r.diferencia));
    poner(res, 'meses', periodo.length + ' (' + nombreMes(periodo[0]) + ' a ' + nombreMes(periodo[periodo.length - 1]) + ')');
  }

  function iniciarPeriodosArriendo(form) {
    var ipc = datosPagina().ipc || {};
    var meses = Object.keys(ipc).sort();
    $$('[data-periodo]', form).forEach(function (boton) {
      boton.addEventListener('click', function () {
        var n = +boton.getAttribute('data-periodo');
        form.elements.desde.value = meses[Math.max(0, meses.length - n)];
        form.elements.hasta.value = meses[meses.length - 1];
        form.dispatchEvent(new Event('change'));
      });
    });
  }

  function calcHipotecario(form, res) {
    var p = datosPagina().parametros;
    var d = leerFormulario(form);
    var valor = leerNumero(d.valor);
    var pie = leerNumero(d.pie) / 100;
    var tasa = leerNumero(d.tasa) / 100;
    var plazo = +d.plazo;
    var seguros = leerNumero(d.seguros) || 0;
    if (isNaN(valor) || valor <= 0 || isNaN(pie) || pie < 0 || pie >= 1 || isNaN(tasa) || tasa < 0) {
      poner(res, 'dividendo_uf', '—');
      return;
    }
    var r = L.simularHipotecario(valor, pie, tasa, plazo, p, seguros);
    poner(res, 'dividendo_uf', numero(r.dividendo_total_uf, 2) + ' UF');
    poner(res, 'dividendo_pesos', pesos(r.dividendo_pesos));
    poner(res, 'credito', numero(r.credito_uf, 0) + ' UF (' + pesos(r.credito_uf * p.uf) + ')');
    poner(res, 'pie', numero(r.pie_uf, 0) + ' UF (' + pesos(r.pie_uf * p.uf) + ')');
    poner(res, 'renta', pesos(r.renta_minima));
    poner(res, 'intereses', numero(r.intereses_uf, 0) + ' UF');
    poner(res, 'total', numero(r.total_pagado_uf, 0) + ' UF');
    var cuerpo = $('[data-r="saldos"]', res);
    if (cuerpo) {
      cuerpo.innerHTML = L.saldosAnuales(r.credito_uf, tasa, plazo).map(function (fila) {
        return '<tr><td>' + fila.anio + '</td><td class="num">' + numero(fila.intereses, 1) +
          '</td><td class="num">' + numero(fila.amortizacion, 1) + '</td><td class="num">' +
          numero(fila.saldo, 1) + '</td></tr>';
      }).join('');
    }
  }

  function graficoAhorro(serie) {
    var ancho = 320;
    var alto = 160;
    var maximo = serie[serie.length - 1].saldo || 1;
    var paso = ancho / serie.length;
    var barras = serie.map(function (punto, i) {
      var x = i * paso + paso * 0.15;
      var w = paso * 0.7;
      var hTotal = punto.saldo / maximo * (alto - 10);
      var hAporte = Math.min(punto.aportado, punto.saldo) / maximo * (alto - 10);
      return '<rect class="g-barra-aporte" x="' + x.toFixed(1) + '" y="' + (alto - hAporte).toFixed(1) +
        '" width="' + w.toFixed(1) + '" height="' + hAporte.toFixed(1) + '"/>' +
        '<rect class="g-barra" x="' + x.toFixed(1) + '" y="' + (alto - hTotal).toFixed(1) +
        '" width="' + w.toFixed(1) + '" height="' + Math.max(0, hTotal - hAporte).toFixed(1) + '"/>';
    }).join('');
    return '<svg class="grafico" viewBox="0 0 ' + ancho + ' ' + alto + '">' + barras + '</svg>' +
      '<p class="leyenda"><span class="muestra muestra-aporte"></span>Aportes <span class="muestra"></span>Intereses</p>';
  }

  function calcAhorro(form, res) {
    var d = leerFormulario(form);
    var inicial = leerNumero(d.inicial) || 0;
    var aporte = leerNumero(d.aporte) || 0;
    var tasa = leerNumero(d.tasa) / 100;
    var anios = Math.min(80, Math.max(1, Math.round(leerNumero(d.anios) || 0)));
    if (isNaN(tasa) || tasa <= -1) {
      poner(res, 'saldo', '—');
      return;
    }
    var r = L.proyectarAhorro(inicial, aporte, tasa, anios);
    poner(res, 'saldo', pesos(r.saldo));
    poner(res, 'aportado', pesos(r.aportado));
    poner(res, 'ganancia', pesos(r.ganancia));
    var grafico = $('[data-r="grafico"]', res);
    if (grafico) {
      grafico.innerHTML = graficoAhorro(r.serie);
    }
  }

  function calcDias(form, res) {
    var datos = datosPagina();
    var lista = datos.feriados || [];
    var fechas = lista.map(function (f) { return f.fecha; });
    var nombres = {};
    lista.forEach(function (f) { nombres[f.fecha] = f.nombre; });
    var d = leerFormulario(form);
    var contar = d.modo !== 'sumar';
    alternar(form, '[data-solo-contar]', contar);
    alternar(form, '[data-solo-sumar]', !contar);
    var minimo = datos.anios[0] + '-01-01';
    var maximo = datos.anios[datos.anios.length - 1] + '-12-31';
    var listaFeriados = $('[data-r="feriados"]', res);
    var r;
    if (!d.inicio || d.inicio < minimo || d.inicio > maximo) {
      poner(res, 'principal', '—');
      poner(res, 'detalle', 'Elige fechas entre ' + fechaLarga(minimo) + ' y ' + fechaLarga(maximo) + '.');
      return;
    }
    if (contar) {
      if (!d.fin || d.fin > maximo) {
        poner(res, 'principal', '—');
        return;
      }
      var inicio = d.inicio <= d.fin ? d.inicio : d.fin;
      var fin = d.inicio <= d.fin ? d.fin : d.inicio;
      r = L.contarDiasHabiles(inicio, fin, fechas, d.sabados, d.incluir_inicio);
      poner(res, 'etiqueta', 'Días hábiles');
      poner(res, 'principal', String(r.dias));
      poner(res, 'detalle', 'Entre el ' + fechaLarga(inicio, true) + ' y el ' + fechaLarga(fin, true) + '.');
    } else {
      var cantidad = Math.round(leerNumero(d.cantidad));
      if (isNaN(cantidad) || cantidad < 1 || cantidad > 500) {
        poner(res, 'principal', '—');
        return;
      }
      r = L.sumarDiasHabiles(d.inicio, cantidad, fechas, d.sabados);
      if (r.fecha > maximo) {
        poner(res, 'principal', '—');
        poner(res, 'detalle', 'El resultado queda fuera del rango de feriados disponible.');
        return;
      }
      poner(res, 'etiqueta', 'Fecha resultante');
      poner(res, 'principal', capitalizar(fechaLarga(r.fecha, true)));
      poner(res, 'detalle', cantidad + ' días hábiles después del ' + fechaLarga(d.inicio) + '.');
    }
    if (listaFeriados) {
      listaFeriados.innerHTML = '';
      r.feriados.forEach(function (fecha) {
        var item = document.createElement('li');
        item.textContent = 'Se excluye el feriado del ' + fechaLarga(fecha, true) + ': ' + (nombres[fecha] || 'feriado');
        listaFeriados.appendChild(item);
      });
    }
  }

  /** Lee y valida las fechas de los formularios de finiquito y vacaciones. */
  function fechasContrato(d, res, datos) {
    var rango = datos.rango || ['1900-01-01', '2999-12-31'];
    if (!d.inicio || !d.termino || d.inicio > d.termino) {
      poner(res, 'principal', '—');
      return false;
    }
    if (d.termino < rango[0] || d.termino > rango[1]) {
      poner(res, 'principal', '—');
      return false;
    }
    return true;
  }

  function textoTiempo(t) {
    var partes = [];
    if (t.anios) {
      partes.push(t.anios + (t.anios === 1 ? ' año' : ' años'));
    }
    partes.push(t.meses + (t.meses === 1 ? ' mes' : ' meses'));
    partes.push(t.dias + (t.dias === 1 ? ' día' : ' días'));
    return partes.join(', ');
  }

  function calcFiniquito(form, res) {
    var datos = datosPagina();
    var d = leerFormulario(form);
    var conIndemnizacion = d.causal === 'necesidades_empresa' || d.causal === 'desahucio';
    alternar(form, '[data-solo-indemnizacion]', conIndemnizacion);
    var remuneracion = leerNumero(d.remuneracion);
    if (!fechasContrato(d, res, datos) || isNaN(remuneracion) || remuneracion <= 0) {
      return;
    }
    var r = L.finiquito(d.inicio, d.termino, remuneracion, d.causal, datos.parametros, datos.feriados,
      !!d.aviso, leerNumero(d.pendientes) || 0, leerNumero(d.dias) || 0);
    poner(res, 'principal', pesos(r.total));
    poner(res, 'tiempo', textoTiempo(r.tiempo));
    poner(res, 'anios', '(' + r.anios_indemnizacion + (r.anios_indemnizacion === 1 ? ' año)' : ' años)'));
    poner(res, 'indemnizacion', pesos(r.indemnizacion_anios));
    mostrarFila(res, 'indemnizacion', conIndemnizacion);
    poner(res, 'aviso', pesos(r.aviso_previo));
    mostrarFila(res, 'aviso', conIndemnizacion);
    poner(res, 'feriado_detalle', '(' + numero(r.feriado_habiles, 2) + ' días hábiles = ' +
      numero(r.feriado_corridos, 2) + ' días corridos)');
    poner(res, 'feriado', pesos(r.feriado));
    poner(res, 'pendiente', pesos(r.remuneracion_pendiente));
    mostrarFila(res, 'pendiente', r.remuneracion_pendiente > 0);
    poner(res, 'total', pesos(r.total));
    var nota = 'Para las indemnizaciones, la remuneración se considera con un tope de ' +
      numero(datos.parametros.tope_indemnizacion_uf) + ' UF (' +
      pesos(datos.parametros.tope_indemnizacion_uf * datos.parametros.uf) + ').';
    if (conIndemnizacion && r.anios_indemnizacion === 0) {
      nota = 'La indemnización por años de servicio exige al menos un año de contrato.';
    } else if (r.tope_aplicado) {
      nota += ' Se aplicó el tope.';
    }
    poner(res, 'nota', nota);
  }

  function calcVacaciones(form, res) {
    var datos = datosPagina();
    var d = leerFormulario(form);
    var remuneracion = leerNumero(d.remuneracion);
    if (!fechasContrato(d, res, datos) || isNaN(remuneracion) || remuneracion <= 0) {
      return;
    }
    var proporcional = L.feriadoProporcional(d.inicio, d.termino, datos.parametros);
    var r = L.finiquito(d.inicio, d.termino, remuneracion, 'renuncia', datos.parametros, datos.feriados,
      true, leerNumero(d.pendientes) || 0, 0);
    poner(res, 'principal', pesos(r.feriado));
    poner(res, 'periodo', textoTiempo({ anios: 0, meses: proporcional.meses, dias: proporcional.dias }));
    poner(res, 'proporcionales', numero(r.feriado_proporcional_habiles, 2));
    poner(res, 'habiles', numero(r.feriado_habiles, 2));
    poner(res, 'inhabiles', String(r.feriado_inhabiles));
    poner(res, 'corridos', numero(r.feriado_corridos, 2));
  }

  // ---------------------------------------------------------------------------
  // Próximo feriado y proyección de UF
  // ---------------------------------------------------------------------------

  function actualizarProximoFeriado() {
    var caja = $('[data-proximo-feriado]');
    var datos = datosPagina();
    if (!caja || !datos.feriados) {
      return;
    }
    var hoy = hoyChile();
    var futuros = datos.feriados.filter(function (f) { return f.fecha >= hoy; });
    futuros.sort(function (a, b) { return a.fecha < b.fecha ? -1 : 1; });
    if (!futuros.length) {
      return;
    }
    var proximo = futuros[0];
    var dias = Math.round((aFechaUTC(proximo.fecha) - aFechaUTC(hoy)) / 86400000);
    var etiqueta = $('.destacado-etiqueta', caja);
    etiqueta.textContent = dias === 0 ? 'Hoy es feriado' :
      'Próximo feriado: ' + (dias === 1 ? 'mañana' : 'faltan ' + dias + ' días');
    poner(caja, 'nombre', proximo.nombre);
    poner(caja, 'fecha', capitalizar(fechaLarga(proximo.fecha, true)));
  }

  function iniciarProyeccion() {
    var input = $('[data-proyeccion-monto]');
    if (!input) {
      return;
    }
    input.addEventListener('input', function () {
      var monto = leerNumero(input.value);
      $$('[data-tabla-proyeccion] td[data-uf]').forEach(function (celda) {
        var uf = parseFloat(celda.getAttribute('data-uf'));
        var texto = isNaN(monto) ? '—' : pesos(monto * uf, monto === 1 ? 2 : 0);
        var destino = celda.querySelector('strong') || celda;
        destino.textContent = texto;
      });
    });
  }

  // ---------------------------------------------------------------------------
  // Inicio
  // ---------------------------------------------------------------------------

  function iniciar() {
    iniciarConversores();
    actualizarUf();
    actualizarProximoFeriado();
    iniciarProyeccion();
    if (!L) {
      return;
    }
    var calculadoras = {
      sueldo: [calcSueldo, 'resultado-sueldo'],
      honorarios: [calcHonorarios, 'resultado-honorarios'],
      arriendo: [calcArriendo, 'resultado-arriendo'],
      hipotecario: [calcHipotecario, 'resultado-hipotecario'],
      ahorro: [calcAhorro, 'resultado-ahorro'],
      dias: [calcDias, 'resultado-dias'],
      finiquito: [calcFiniquito, 'resultado-finiquito'],
      vacaciones: [calcVacaciones, 'resultado-vacaciones']
    };
    $$('form[data-calculadora]').forEach(function (form) {
      var definicion = calculadoras[form.getAttribute('data-calculadora')];
      var resultado = definicion && document.getElementById(definicion[1]);
      if (!resultado) {
        return;
      }
      if (form.getAttribute('data-calculadora') === 'arriendo') {
        iniciarPeriodosArriendo(form);
      }
      calculadora(form, resultado, definicion[0]);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();
