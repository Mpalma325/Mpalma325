/*
 * Cálculos de Lucas Claras para el navegador.
 *
 * Replica paso a paso lucas/calculos.py: mismas operaciones y mismo orden, para
 * que Python y JavaScript den exactamente el mismo resultado. Si cambias una
 * fórmula aquí, cámbiala también allá; tests/test_paridad_js.py lo verifica.
 *
 * Funciona en el navegador (window.LucasCalculos) y en Node (module.exports).
 */
(function (raiz, fabrica) {
  'use strict';
  if (typeof module === 'object' && module.exports) {
    module.exports = fabrica();
  } else {
    raiz.LucasCalculos = fabrica();
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  function redondear(valor, decimales) {
    var factor = Math.pow(10, decimales || 0);
    if (valor < 0) {
      return -Math.floor(-valor * factor + 0.5) / factor;
    }
    return Math.floor(valor * factor + 0.5) / factor;
  }

  function afpMasBarata(p) {
    var claves = Object.keys(p.comisiones_afp).sort();
    var mejor = claves[0];
    claves.forEach(function (clave) {
      if (p.comisiones_afp[clave] < p.comisiones_afp[mejor]) {
        mejor = clave;
      }
    });
    return mejor;
  }

  // -------------------------------------------------------------------------
  // Remuneraciones
  // -------------------------------------------------------------------------

  function impuestoUnico(base, p) {
    var utm = p.utm;
    var tramos = p.tramos_impuesto;
    for (var i = 0; i < tramos.length; i++) {
      var tramo = tramos[i];
      if (tramo.hasta === null || base <= tramo.hasta * utm) {
        var impuesto = base * tramo.factor - tramo.rebaja * utm;
        return {
          impuesto: Math.max(0, redondear(impuesto)),
          tramo: i,
          factor: tramo.factor,
          rebaja: tramo.rebaja
        };
      }
    }
    throw new Error('La tabla de impuesto único debe terminar con un tramo sin tope');
  }

  function gratificacionLegal(sueldoBase, p) {
    var tope = p.gratificacion_tope_imm_anual * p.imm / 12;
    return redondear(Math.min(sueldoBase * p.gratificacion_tasa, tope));
  }

  function sueldoLiquido(bruto, p, opciones) {
    var o = opciones || {};
    var afp = o.afp || 'uno';
    var salud = o.salud || 'fonasa';
    var planIsapreUf = o.plan_isapre_uf || 0;
    var contrato = o.contrato || 'indefinido';
    var noImponible = o.no_imponible || 0;
    var apv = o.apv || 0;

    var uf = p.uf_topes;
    var topeAfp = p.tope_imponible_uf * uf;
    var topeAfc = p.tope_cesantia_uf * uf;
    var imponible = Math.min(bruto, topeAfp);
    var imponibleAfc = Math.min(bruto, topeAfc);

    var tasaAfp = p.tasa_afp + p.comisiones_afp[afp];
    var descuentoAfp = redondear(imponible * tasaAfp);
    var saludLegal = redondear(imponible * p.salud_obligatoria);
    var descuentoSalud = saludLegal;
    if (salud === 'isapre') {
      descuentoSalud = Math.max(saludLegal, redondear(planIsapreUf * uf));
    }
    var descuentoAfc = redondear(imponibleAfc * p.cesantia_trabajador[contrato]);

    var apvRebajable = Math.min(apv, redondear(p.tope_apv_mensual_uf * uf));
    var baseTributable = Math.max(0, bruto - descuentoAfp - saludLegal - descuentoAfc - apvRebajable);
    var impuesto = impuestoUnico(baseTributable, p);

    var totalDescuentos = descuentoAfp + descuentoSalud + descuentoAfc + impuesto.impuesto + apv;
    return {
      bruto: bruto,
      no_imponible: noImponible,
      imponible: imponible,
      tope_aplicado: bruto > topeAfp,
      afp: descuentoAfp,
      tasa_afp_total: tasaAfp,
      salud: descuentoSalud,
      salud_adicional: descuentoSalud - saludLegal,
      cesantia: descuentoAfc,
      apv: apv,
      base_tributable: baseTributable,
      impuesto: impuesto.impuesto,
      tramo: impuesto.tramo,
      tasa_marginal: impuesto.factor,
      total_descuentos: totalDescuentos,
      liquido: bruto + noImponible - totalDescuentos
    };
  }

  function brutoParaLiquido(liquidoObjetivo, p, opciones) {
    var bajo = 0;
    var alto = 1000;
    while (sueldoLiquido(alto, p, opciones).liquido < liquidoObjetivo) {
      bajo = alto;
      alto = alto * 2;
    }
    while (alto - bajo > 1) {
      var medio = Math.floor((bajo + alto) / 2);
      if (sueldoLiquido(medio, p, opciones).liquido >= liquidoObjetivo) {
        alto = medio;
      } else {
        bajo = medio;
      }
    }
    return sueldoLiquido(alto, p, opciones);
  }

  function costoEmpleador(bruto, p, contrato, noImponible) {
    contrato = contrato || 'indefinido';
    noImponible = noImponible || 0;
    var uf = p.uf_topes;
    var imponible = Math.min(bruto, p.tope_imponible_uf * uf);
    var imponibleAfc = Math.min(bruto, p.tope_cesantia_uf * uf);
    var sis = redondear(imponible * p.sis);
    var cesantia = redondear(imponibleAfc * p.cesantia_empleador[contrato]);
    var mutual = redondear(imponible * p.mutual_basica);
    var reforma = redondear(imponible * p.aporte_empleador_reforma);
    var total = sis + cesantia + mutual + reforma;
    return {
      sis: sis,
      cesantia: cesantia,
      mutual: mutual,
      reforma: reforma,
      total_cotizaciones: total,
      costo_total: bruto + noImponible + total
    };
  }

  // -------------------------------------------------------------------------
  // Finiquito y vacaciones proporcionales (fechas como texto AAAA-MM-DD)
  // -------------------------------------------------------------------------

  var CAUSALES_CON_INDEMNIZACION = ['necesidades_empresa', 'desahucio'];
  // Término de obra o faena (art. 159 N° 5, Ley 21.122): 2,5 días por mes trabajado.
  var DIAS_POR_MES_OBRA = 2.5;

  function iso(anio, mes, dia) {
    return anio + '-' + ('0' + mes).slice(-2) + '-' + ('0' + dia).slice(-2);
  }

  function diasDelMes(anio, mes) {
    return new Date(Date.UTC(anio, mes, 0)).getUTCDate();
  }

  function sumarMeses(fecha, meses) {
    var p = fecha.split('-');
    var total = +p[1] - 1 + meses;
    var anio = +p[0] + Math.floor(total / 12);
    var mes = ((total % 12) + 12) % 12 + 1;
    return iso(anio, mes, Math.min(+p[2], diasDelMes(anio, mes)));
  }

  function sumarDias(fecha, dias) {
    var d = aFecha(fecha);
    d.setUTCDate(d.getUTCDate() + dias);
    return aTexto(d);
  }

  function tiempoTrabajado(inicio, termino) {
    var hasta = sumarDias(termino, 1);
    var meses = 0;
    while (sumarMeses(inicio, meses + 1) <= hasta) {
      meses += 1;
    }
    var dias = Math.round((aFecha(hasta) - aFecha(sumarMeses(inicio, meses))) / 86400000);
    return { anios: Math.floor(meses / 12), meses: meses % 12, dias: dias, meses_totales: meses };
  }

  function aniosDeServicio(inicio, termino, p) {
    var t = tiempoTrabajado(inicio, termino);
    if (t.anios < 1) {
      return 0;
    }
    var extra = (t.meses > 6 || (t.meses === 6 && t.dias > 0)) ? 1 : 0;
    return Math.min(t.anios + extra, p.tope_anios_indemnizacion);
  }

  function mesesObraOFaena(inicio, termino) {
    var t = tiempoTrabajado(inicio, termino);
    if (t.meses_totales < 1) {
      return 0;
    }
    return t.meses_totales + (t.dias > 15 ? 1 : 0);
  }

  function feriadoProporcional(inicio, termino, p) {
    var anios = tiempoTrabajado(inicio, termino).anios;
    var aniversario = sumarMeses(inicio, 12 * anios);
    var t = tiempoTrabajado(aniversario, termino);
    var porMes = p.feriado_anual_habiles / 12;
    return {
      desde: aniversario,
      meses: t.meses,
      dias: t.dias,
      dias_habiles: porMes * t.meses + porMes / 30 * t.dias
    };
  }

  function diasCorridosDeFeriado(diasHabiles, termino, feriados) {
    var enteros = Math.floor(diasHabiles);
    var fraccion = diasHabiles - enteros;
    var dia = aFecha(termino);
    var corridos = 0;
    var contados = 0;
    while (contados < enteros) {
      dia.setUTCDate(dia.getUTCDate() + 1);
      corridos += 1;
      var semana = dia.getUTCDay();
      if (semana !== 0 && semana !== 6 && feriados.indexOf(aTexto(dia)) === -1) {
        contados += 1;
      }
    }
    return { dias_corridos: corridos + fraccion, inhabiles: corridos - enteros, hasta: aTexto(dia) };
  }

  function finiquito(inicio, termino, remuneracion, causal, p, feriados, avisoDado, diasPendientes, diasPorPagar) {
    avisoDado = avisoDado === undefined ? true : avisoDado;
    diasPendientes = diasPendientes || 0;
    diasPorPagar = diasPorPagar || 0;
    var tope = p.tope_indemnizacion_uf * p.uf_indemnizaciones;
    var base = Math.min(remuneracion, tope);
    var conIndemnizacion = CAUSALES_CON_INDEMNIZACION.indexOf(causal) !== -1;
    var anios = conIndemnizacion ? aniosDeServicio(inicio, termino, p) : 0;
    var indemnizacion = redondear(base * anios);
    var aviso = conIndemnizacion && !avisoDado ? redondear(base) : 0;
    var mesesObra = causal === 'termino_obra' ? mesesObraOFaena(inicio, termino) : 0;
    var indemnizacionObra = redondear(base / 30 * DIAS_POR_MES_OBRA * mesesObra);
    var proporcional = feriadoProporcional(inicio, termino, p);
    var habiles = proporcional.dias_habiles + diasPendientes;
    var conversion = diasCorridosDeFeriado(habiles, termino, feriados);
    var valorDia = remuneracion / 30;
    var feriado = redondear(conversion.dias_corridos * valorDia);
    var remuneracionPendiente = redondear(diasPorPagar * valorDia);
    return {
      tiempo: tiempoTrabajado(inicio, termino),
      anios_indemnizacion: anios,
      tope_aplicado: (conIndemnizacion || causal === 'termino_obra') && remuneracion > tope,
      indemnizacion_anios: indemnizacion,
      aviso_previo: aviso,
      meses_obra: mesesObra,
      indemnizacion_obra: indemnizacionObra,
      feriado_proporcional_habiles: proporcional.dias_habiles,
      feriado_habiles: habiles,
      feriado_corridos: conversion.dias_corridos,
      feriado_inhabiles: conversion.inhabiles,
      feriado: feriado,
      remuneracion_pendiente: remuneracionPendiente,
      total: indemnizacion + aviso + indemnizacionObra + feriado + remuneracionPendiente
    };
  }

  // -------------------------------------------------------------------------
  // Boleta de honorarios
  // -------------------------------------------------------------------------

  function honorariosDesdeBruto(bruto, p) {
    var tasa = p.retencion_honorarios;
    var retencion = redondear(bruto * tasa);
    return { bruto: bruto, retencion: retencion, liquido: bruto - retencion, tasa: tasa };
  }

  function honorariosDesdeLiquido(liquido, p) {
    var tasa = p.retencion_honorarios;
    var bruto = redondear(liquido / (1 - tasa));
    while (bruto - redondear(bruto * tasa) < liquido) {
      bruto += 1;
    }
    while (bruto > 0 && (bruto - 1) - redondear((bruto - 1) * tasa) >= liquido) {
      bruto -= 1;
    }
    return honorariosDesdeBruto(bruto, p);
  }

  // -------------------------------------------------------------------------
  // Crédito hipotecario
  // -------------------------------------------------------------------------

  function dividendo(monto, tasaAnual, anios) {
    var n = Math.round(anios * 12);
    var r = tasaAnual / 12;
    if (r === 0) {
      return monto / n;
    }
    return monto * r / (1 - Math.pow(1 + r, -n));
  }

  function simularHipotecario(valorUf, pie, tasaAnual, anios, p, segurosUf) {
    segurosUf = segurosUf || 0;
    var pieUf = valorUf * pie;
    var creditoUf = valorUf - pieUf;
    var cuotaUf = dividendo(creditoUf, tasaAnual, anios);
    var totalCuotasUf = cuotaUf * Math.round(anios * 12);
    var dividendoTotalUf = cuotaUf + segurosUf;
    var dividendoPesos = redondear(dividendoTotalUf * p.uf);
    return {
      pie_uf: pieUf,
      credito_uf: creditoUf,
      dividendo_uf: cuotaUf,
      dividendo_total_uf: dividendoTotalUf,
      dividendo_pesos: dividendoPesos,
      intereses_uf: totalCuotasUf - creditoUf,
      total_pagado_uf: totalCuotasUf,
      renta_minima: redondear(dividendoPesos / p.carga_financiera_maxima)
    };
  }

  function saldosAnuales(credito, tasaAnual, anios) {
    var n = Math.round(anios * 12);
    var r = tasaAnual / 12;
    var cuota = dividendo(credito, tasaAnual, anios);
    var saldo = credito;
    var filas = [];
    var interesesAnio = 0;
    var amortizacionAnio = 0;
    for (var mes = 1; mes <= n; mes++) {
      var interes = saldo * r;
      var amortizacion = cuota - interes;
      saldo -= amortizacion;
      interesesAnio += interes;
      amortizacionAnio += amortizacion;
      if (mes % 12 === 0 || mes === n) {
        filas.push({
          anio: Math.floor((mes + 11) / 12),
          intereses: interesesAnio,
          amortizacion: amortizacionAnio,
          saldo: Math.max(0, saldo)
        });
        interesesAnio = 0;
        amortizacionAnio = 0;
      }
    }
    return filas;
  }

  // -------------------------------------------------------------------------
  // IPC, ahorro y conversiones
  // -------------------------------------------------------------------------

  function variacionAcumulada(variaciones) {
    var factor = 1;
    variaciones.forEach(function (v) {
      factor *= 1 + v;
    });
    return factor - 1;
  }

  function reajustarPorIpc(monto, variaciones) {
    var variacion = variacionAcumulada(variaciones);
    var nuevo = redondear(monto * (1 + variacion));
    return { variacion: variacion, nuevo_monto: nuevo, diferencia: nuevo - monto };
  }

  function proyectarAhorro(inicial, aporteMensual, tasaAnual, anios) {
    var r = Math.pow(1 + tasaAnual, 1 / 12) - 1;
    var saldo = inicial;
    var aportado = inicial;
    var serie = [{ anio: 0, saldo: saldo, aportado: aportado }];
    var meses = Math.round(anios * 12);
    for (var mes = 1; mes <= meses; mes++) {
      saldo = saldo * (1 + r) + aporteMensual;
      aportado += aporteMensual;
      if (mes % 12 === 0 || mes === meses) {
        serie.push({ anio: mes / 12, saldo: saldo, aportado: aportado });
      }
    }
    return { saldo: saldo, aportado: aportado, ganancia: saldo - aportado, serie: serie };
  }

  // -------------------------------------------------------------------------
  // Días hábiles
  // -------------------------------------------------------------------------

  function aFecha(texto) {
    var partes = texto.split('-');
    return new Date(Date.UTC(+partes[0], +partes[1] - 1, +partes[2]));
  }

  function aTexto(fecha) {
    return fecha.toISOString().slice(0, 10);
  }

  function esHabil(fecha, feriados, sabados) {
    var dia = fecha.getUTCDay(); // 0 = domingo
    if (dia === 0 || (dia === 6 && !sabados)) {
      return false;
    }
    return feriados.indexOf(aTexto(fecha)) === -1;
  }

  function contarDiasHabiles(inicio, fin, feriados, sabados, incluirInicio) {
    var desde = aFecha(inicio);
    var hasta = aFecha(fin);
    var cuenta = 0;
    var excluidos = [];
    if (!incluirInicio) {
      desde.setUTCDate(desde.getUTCDate() + 1);
    }
    for (var d = new Date(desde); d <= hasta; d.setUTCDate(d.getUTCDate() + 1)) {
      if (esHabil(d, feriados, sabados)) {
        cuenta += 1;
      } else if (feriados.indexOf(aTexto(d)) !== -1) {
        excluidos.push(aTexto(d));
      }
    }
    return { dias: cuenta, feriados: excluidos };
  }

  function sumarDiasHabiles(inicio, cantidad, feriados, sabados) {
    var fecha = aFecha(inicio);
    var excluidos = [];
    var sumados = 0;
    while (sumados < cantidad) {
      fecha.setUTCDate(fecha.getUTCDate() + 1);
      if (esHabil(fecha, feriados, sabados)) {
        sumados += 1;
      } else if (feriados.indexOf(aTexto(fecha)) !== -1) {
        excluidos.push(aTexto(fecha));
      }
    }
    return { fecha: aTexto(fecha), feriados: excluidos };
  }

  // -------------------------------------------------------------------------
  // IVA (montos en pesos enteros)
  // -------------------------------------------------------------------------

  function ivaDesdeNeto(neto, p) {
    var tasa = p.iva;
    neto = redondear(neto);
    var iva = redondear(neto * tasa);
    return { neto: neto, iva: iva, total: neto + iva, tasa: tasa };
  }

  function ivaDesdeTotal(total, p) {
    var tasa = p.iva;
    total = redondear(total);
    var neto = redondear(total / (1 + tasa));
    return { neto: neto, iva: total - neto, total: total, tasa: tasa };
  }

  // -------------------------------------------------------------------------
  // Horas extra
  // -------------------------------------------------------------------------

  function factorHorasExtra(jornada, p) {
    return (1 + p.recargo_horas_extra) * 28 / (30 * 4 * jornada);
  }

  function horasExtra(sueldo, horas, jornada, p) {
    var minimo = p.imm * Math.min(1, jornada / p.jornada_semanal_horas);
    var base = Math.max(sueldo, minimo);
    var valorHora = base / 30 * 28 / (4 * jornada);
    var valorExtra = valorHora * (1 + p.recargo_horas_extra);
    return {
      sueldo: sueldo,
      base: base,
      minimo: minimo,
      minimo_aplicado: sueldo < minimo,
      valor_hora: valorHora,
      valor_hora_extra: valorExtra,
      factor: factorHorasExtra(jornada, p),
      horas: horas,
      total: redondear(valorExtra * horas)
    };
  }

  // -------------------------------------------------------------------------
  // Crédito de consumo
  // -------------------------------------------------------------------------

  function tasaTimbres(meses, p) {
    return Math.min(p.timbres_tasa_mensual * meses, p.timbres_tope);
  }

  function cuotaFrancesa(capital, tasaMensual, meses) {
    if (tasaMensual === 0) {
      return capital / meses;
    }
    var factor = 1;
    for (var i = 0; i < meses; i++) {
      factor *= 1 + tasaMensual;
    }
    return capital * tasaMensual * factor / (factor - 1);
  }

  function valorPresente(flujos, tasaMensual) {
    var total = 0;
    var descuento = 1;
    for (var i = 0; i < flujos.length; i++) {
      descuento /= 1 + tasaMensual;
      total += flujos[i] * descuento;
    }
    return total;
  }

  function cargaAnualEquivalente(montoLiquido, flujos) {
    if (montoLiquido <= 0) {
      throw new Error('Lo que se paga al firmar no puede igualar o superar el monto del crédito');
    }
    var bajo = 0;
    var alto = 1;
    while (valorPresente(flujos, alto) > montoLiquido && alto < 1e6) {
      alto *= 2;
    }
    for (var paso = 0; paso < 100; paso++) {
      var medio = (bajo + alto) / 2;
      if (valorPresente(flujos, medio) > montoLiquido) {
        bajo = medio;
      } else {
        alto = medio;
      }
    }
    return 12 * (bajo + alto) / 2;
  }

  function creditoConsumo(monto, meses, tasaMensual, p, seguros, gastos, financiar) {
    monto = redondear(monto);
    seguros = redondear(seguros || 0);
    gastos = redondear(gastos || 0);
    financiar = financiar === undefined ? true : financiar;
    var tasaImpuesto = tasaTimbres(meses, p);
    var bruto;
    var impuesto;
    var alContado;
    if (financiar) {
      bruto = redondear((monto + gastos) / (1 - tasaImpuesto));
      impuesto = bruto - monto - gastos;
      alContado = 0;
    } else {
      bruto = monto;
      impuesto = redondear(monto * tasaImpuesto);
      alContado = impuesto + gastos;
    }
    var cuota = redondear(cuotaFrancesa(bruto, tasaMensual, meses));
    var cuotaTotal = cuota + seguros;
    var totalCuotas = cuotaTotal * meses;
    var costoTotal = totalCuotas + alContado;
    var flujos = [];
    for (var i = 0; i < meses; i++) {
      flujos.push(cuotaTotal);
    }
    return {
      monto_liquido: monto,
      monto_bruto: bruto,
      meses: meses,
      tasa_mensual: tasaMensual,
      tasa_impuesto: tasaImpuesto,
      impuesto: impuesto,
      gastos: gastos,
      al_contado: alContado,
      cuota: cuota,
      seguros: seguros,
      cuota_total: cuotaTotal,
      total_cuotas: totalCuotas,
      intereses: cuota * meses - bruto,
      total_seguros: seguros * meses,
      costo_total: costoTotal,
      sobrecosto: costoTotal - monto,
      cae: cargaAnualEquivalente(monto - alContado, flujos)
    };
  }

  return {
    redondear: redondear,
    afpMasBarata: afpMasBarata,
    impuestoUnico: impuestoUnico,
    gratificacionLegal: gratificacionLegal,
    sueldoLiquido: sueldoLiquido,
    brutoParaLiquido: brutoParaLiquido,
    costoEmpleador: costoEmpleador,
    sumarMeses: sumarMeses,
    tiempoTrabajado: tiempoTrabajado,
    aniosDeServicio: aniosDeServicio,
    mesesObraOFaena: mesesObraOFaena,
    feriadoProporcional: feriadoProporcional,
    diasCorridosDeFeriado: diasCorridosDeFeriado,
    finiquito: finiquito,
    honorariosDesdeBruto: honorariosDesdeBruto,
    honorariosDesdeLiquido: honorariosDesdeLiquido,
    dividendo: dividendo,
    simularHipotecario: simularHipotecario,
    saldosAnuales: saldosAnuales,
    variacionAcumulada: variacionAcumulada,
    reajustarPorIpc: reajustarPorIpc,
    proyectarAhorro: proyectarAhorro,
    contarDiasHabiles: contarDiasHabiles,
    sumarDiasHabiles: sumarDiasHabiles,
    ivaDesdeNeto: ivaDesdeNeto,
    ivaDesdeTotal: ivaDesdeTotal,
    factorHorasExtra: factorHorasExtra,
    horasExtra: horasExtra,
    tasaTimbres: tasaTimbres,
    cuotaFrancesa: cuotaFrancesa,
    valorPresente: valorPresente,
    cargaAnualEquivalente: cargaAnualEquivalente,
    creditoConsumo: creditoConsumo
  };
});
