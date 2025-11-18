// src/pages/reportes/Reportes.jsx
import { useState, useEffect, useRef } from 'react';
import api from '../../api/axios.js';
import { Mic, StopCircle, Download, Eye, Loader2, Info } from 'lucide-react';

const EXAMPLES = [
  {
    label: 'Ventas por cliente (mes actual)',
    text: 'Reporte de ventas de este mes agrupado por cliente en pantalla',
  },
  {
    label: 'Productos comprados por un cliente',
    text: 'Productos comprados por el cliente Juan Pérez del 01/11/2025 al 30/11/2025 agrupados por producto en pantalla',
  },
  {
    label: 'Top productos del mes',
    text: 'Top 10 productos más vendidos de este mes por monto en pantalla',
  },
  {
    label: 'Stock bajo (< 5 unidades)',
    text: 'Productos con stock menor a 5 unidades ordenados por stock ascendente en pantalla',
  },
  {
    label: 'Lista de precios por categoría',
    text: 'Lista de precios de productos de la categoría Electrodomésticos en pantalla',
  },
  {
    label: 'Productos sin movimiento',
    text: 'Productos sin movimiento de ventas en los últimos 3 meses en pantalla',
  },
];

export default function Reportes() {
  const [prompt, setPrompt] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [supportsVoice, setSupportsVoice] = useState(true);

  const [isLoading, setIsLoading] = useState(false);
  const [loadingAction, setLoadingAction] = useState(null); // "preview" | "download" | null

  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [previewData, setPreviewData] = useState(null);

  const recRef = useRef(null);

  // -----------------------------
  // Configuración de voz
  // -----------------------------
  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      setSupportsVoice(false);
      return;
    }

    const recognition = new SR();
    recognition.continuous = false;
    recognition.lang = 'es-ES';
    recognition.interimResults = false;

    recognition.onresult = async (evt) => {
      const t = evt.results?.[0]?.[0]?.transcript || '';
      setPrompt(t);

      // Auto-previsualizar en pantalla (quitamos "en pdf/excel")
      try {
        setIsLoading(true);
        setLoadingAction('preview');
        setError(null);
        setPreviewData(null);
        setSuccessMessage(null);

        const clean = t.replace(/\b(en\s+)?(pdf|excel|xlsx)\b/gi, '').trim();
        if (clean) {
          const r = await api.post('reportes/prompt/', { prompt: clean });
          setPreviewData(r.data);
        }
      } catch (err) {
        setError(
          err?.response?.data?.error ||
            err?.response?.data?.detail ||
            'No pude previsualizar el reporte.'
        );
      } finally {
        setIsLoading(false);
        setLoadingAction(null);
        setIsListening(false);
      }
    };

    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recRef.current = recognition;
  }, []);

  const handleListen = () => {
    if (!recRef.current) {
      alert('El reconocimiento de voz no es compatible con este navegador.');
      return;
    }
    setPreviewData(null);
    setError(null);
    setSuccessMessage(null);
    recRef.current.start();
    setIsListening(true);
  };

  const stopListen = () => {
    try {
      recRef.current?.stop();
    } catch (_) {}
    setIsListening(false);
  };

  // Limpieza automática de mensajes
  useEffect(() => {
    if (error || successMessage) {
      const timer = setTimeout(() => {
        setError(null);
        setSuccessMessage(null);
      }, 4500);
      return () => clearTimeout(timer);
    }
  }, [error, successMessage]);

  // -----------------------------
  // Acciones
  // -----------------------------
  const handlePreview = async (e) => {
    e?.preventDefault?.();
    if (!prompt.trim()) return;

    setIsLoading(true);
    setLoadingAction('preview');
    setError(null);
    setPreviewData(null);
    setSuccessMessage(null);

    try {
      // Para previsualizar siempre forzamos "en pantalla"
      const previewPrompt = prompt
        .replace(/\b(en\s+)?(pdf|excel|xlsx)\b/gi, '')
        .trim();
      const response = await api.post('reportes/prompt/', {
        prompt: previewPrompt,
      });
      setPreviewData(response.data);
    } catch (err) {
      setError(
        err.response?.data?.error ||
          err.response?.data?.detail ||
          'Ocurrió un error al previsualizar.'
      );
    } finally {
      setIsLoading(false);
      setLoadingAction(null);
    }
  };

  const handleDownload = async (e) => {
    e?.preventDefault?.();
    if (!prompt.trim()) return;

    if (!/pdf|excel|xlsx/i.test(prompt)) {
      setError("Para descargar, especifica 'en PDF' o 'en Excel' en el prompt.");
      return;
    }

    setIsLoading(true);
    setLoadingAction('download');
    setError(null);
    setPreviewData(null);
    setSuccessMessage(null);

    try {
      const response = await api.post(
        'reportes/prompt/',
        { prompt },
        { responseType: 'blob' }
      );

      const ext = /pdf/i.test(prompt) ? 'pdf' : 'xlsx';
      const filename = `reporte-${new Date().toISOString().slice(0, 10)}.${ext}`;

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setSuccessMessage(`¡Reporte "${filename}" descargado con éxito!`);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.response?.data?.error ||
          'Ocurrió un error al descargar el archivo.'
      );
    } finally {
      setIsLoading(false);
      setLoadingAction(null);
    }
  };

  // -----------------------------
  // Render
  // -----------------------------
  const headers = previewData?.headers || [];
  const rows = previewData?.rows || [];
  const meta = previewData?.meta || {};
  const hints = previewData?.hints || [];
  const warnings = previewData?.warnings || [];

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 lg:py-8">
      {/* Encabezado */}
      <div className="mb-5 lg:mb-8">
        <h1 className="text-2xl lg:text-3xl font-semibold text-neutral-100 tracking-tight">
          Generador de reportes
        </h1>
        <p className="mt-2 text-sm lg:text-base text-neutral-400 max-w-2xl">
          Escribe o dicta lo que necesitas y el sistema generará el reporte
          consultando varias tablas (ventas, clientes, productos, stock, etc.).
        </p>
      </div>

      {/* Layout principal: prompt + preview */}
      <div className="grid gap-5 lg:gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1.2fr)]">
        {/* Panel de entrada */}
        <div className="bg-neutral-900/40 border border-neutral-800 rounded-2xl p-4 sm:p-5 shadow-lg flex flex-col h-full">
          <div className="flex items-center justify-between gap-2 mb-4">
            <h2 className="text-sm font-medium text-neutral-200 flex items-center gap-2">
              <Eye size={16} className="text-cyan-400" />
              Instrucción del reporte
            </h2>
            <span className="text-[11px] px-2 py-1 rounded-full bg-neutral-800/80 text-neutral-400">
              Ej: “Top 10 productos más vendidos de este mes en PDF”
            </span>
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex flex-col sm:flex-row gap-2">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe el reporte que quieres generar..."
                disabled={isLoading && loadingAction === 'download'}
                rows={4}
                className="flex-1 min-h-[120px] rounded-xl bg-neutral-950 border border-neutral-800 focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 text-neutral-200 text-sm p-3 outline-none placeholder:text-neutral-500 resize-none"
              />

              {/* Botón de voz */}
              {supportsVoice && (
                <button
                  type="button"
                  onClick={isListening ? stopListen : handleListen}
                  disabled={isLoading}
                  className={`flex-shrink-0 h-11 w-full sm:w-12 sm:h-[46px] rounded-xl border text-sm sm:text-base grid place-items-center transition
                    ${
                      isListening
                        ? 'border-red-500/60 bg-red-600/20 text-red-200'
                        : 'border-neutral-700 bg-neutral-950 hover:bg-neutral-900 text-neutral-200'
                    }
                    ${isLoading ? 'opacity-60 cursor-not-allowed' : ''}
                  `}
                >
                  {isListening ? <StopCircle size={18} /> : <Mic size={18} />}
                </button>
              )}
            </div>

            {/* Chips de ejemplos */}
            <div className="mt-2 flex flex-wrap gap-2">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex.label}
                  type="button"
                  onClick={() => setPrompt(ex.text)}
                  className="text-[11px] sm:text-xs px-2.5 py-1 rounded-full border border-neutral-700/80 text-neutral-300 bg-neutral-950/60 hover:bg-neutral-900/90 transition"
                >
                  {ex.label}
                </button>
              ))}
            </div>
          </div>

          {/* Botones de acción */}
          <div className="mt-4 flex flex-col sm:flex-row gap-2">
            <button
              type="button"
              onClick={handlePreview}
              disabled={(isLoading && loadingAction === 'download') || !prompt.trim()}
              className="inline-flex justify-center items-center gap-2 px-4 py-2 rounded-xl border border-neutral-700 bg-neutral-950 hover:bg-neutral-900 text-neutral-100 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading && loadingAction === 'preview' ? (
                <Loader2 className="animate-spin" size={18} />
              ) : (
                <Eye size={18} />
              )}
              <span>Previsualizar</span>
            </button>

            <button
              type="button"
              onClick={handleDownload}
              disabled={(isLoading && loadingAction === 'preview') || !prompt.trim()}
              className="inline-flex justify-center items-center gap-2 px-4 py-2 rounded-xl bg-cyan-500 text-neutral-900 font-medium text-sm hover:bg-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading && loadingAction === 'download' ? (
                <Loader2 className="animate-spin" size={18} />
              ) : (
                <Download size={18} />
              )}
              <span>Descargar</span>
            </button>
          </div>

          {/* Mensajes de estado */}
          {error && (
            <div className="mt-4 text-xs sm:text-sm text-red-300 bg-red-600/10 border border-red-900/40 rounded-xl p-3">
              {error}
            </div>
          )}
          {successMessage && (
            <div className="mt-4 text-xs sm:text-sm text-emerald-300 bg-emerald-600/10 border border-emerald-900/40 rounded-xl p-3">
              {successMessage}
            </div>
          )}

          {/* Tips rápidos */}
          <div className="mt-4 text-[11px] sm:text-xs text-neutral-400 flex items-start gap-2">
            <Info size={14} className="mt-0.5 flex-shrink-0 text-neutral-500" />
            <div>
              <div>
                Para descargar, incluye al final <span className="font-semibold">'en PDF'</span> o{' '}
                <span className="font-semibold">'en Excel'</span>.
              </div>
              <div>
                Si no indicas rango de fechas, el sistema usa los últimos 30 días.
              </div>
            </div>
          </div>
        </div>

        {/* Panel de previsualización */}
        <div className="bg-neutral-900/40 border border-neutral-800 rounded-2xl p-4 sm:p-5 shadow-lg flex flex-col h-full">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-neutral-200">
              Previsualización
            </h3>
            <span className="text-[11px] text-neutral-500">
              Solo se muestra al usar “Previsualizar”
            </span>
          </div>

          {/* Meta del reporte */}
          {previewData ? (
            <>
              <div className="mb-3 flex flex-wrap gap-2 text-[11px] text-neutral-400">
                {meta?.intent && (
                  <span className="px-2 py-1 rounded-full bg-neutral-950/80 border border-neutral-800">
                    Intento: <span className="font-semibold">{meta.intent}</span>
                  </span>
                )}
                {meta?.start_date && meta?.end_date && (
                  <span className="px-2 py-1 rounded-full bg-neutral-950/80 border border-neutral-800">
                    Rango: {meta.start_date} — {meta.end_date}
                  </span>
                )}
                {meta?.dimensions && (
                  <span className="px-2 py-1 rounded-full bg-neutral-950/80 border border-neutral-800">
                    Grupo:{' '}
                    {Array.isArray(meta.dimensions)
                      ? meta.dimensions.join(', ')
                      : meta.dimensions}
                  </span>
                )}
              </div>

              {(hints.length > 0 || warnings.length > 0) && (
                <div className="mb-3 space-y-1 text-[11px] text-neutral-400">
                  {hints.map((h, i) => (
                    <div key={`hint-${i}`} className="flex gap-1">
                      <span className="mt-[2px] text-cyan-400">•</span>
                      <span>{h}</span>
                    </div>
                  ))}
                  {warnings.map((w, i) => (
                    <div key={`warn-${i}`} className="flex gap-1 text-amber-300">
                      <span className="mt-[2px]">•</span>
                      <span>{w}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Tabla */}
              <div className="relative flex-1 min-h-[180px] border border-neutral-800/70 rounded-xl bg-neutral-950/80 overflow-hidden">
                <div className="overflow-x-auto max-h-[420px]">
                  <table className="min-w-full text-[11px] sm:text-xs">
                    <thead className="bg-neutral-950 sticky top-0 z-10">
                      <tr className="text-neutral-400">
                        {headers.length > 0 ? (
                          headers.map((h) => (
                            <th
                              key={h}
                              className="text-left px-3 py-2 border-b border-neutral-800"
                            >
                              {h}
                            </th>
                          ))
                        ) : (
                          <th className="px-3 py-2 border-b border-neutral-800">
                            Resultado
                          </th>
                        )}
                      </tr>
                    </thead>
                    <tbody>
                      {rows.length > 0 ? (
                        rows.map((row, i) => (
                          <tr
                            key={i}
                            className={i % 2 === 0 ? 'bg-neutral-900/40' : ''}
                          >
                            {row.map((cell, j) => {
                              const header = headers[j] || '';
                              const alignRight = /monto|total|precio|cantidad/i.test(
                                header
                              );
                              return (
                                <td
                                  key={j}
                                  className={`px-3 py-2 whitespace-nowrap ${
                                    alignRight ? 'text-right' : ''
                                  }`}
                                >
                                  {cell}
                                </td>
                              );
                            })}
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td
                            className="px-3 py-6 text-neutral-400 text-center"
                            colSpan={headers.length || 1}
                          >
                            No se encontraron resultados para este reporte.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-center text-neutral-500 text-xs sm:text-sm border border-dashed border-neutral-800 rounded-xl bg-neutral-950/40 px-4 py-8">
              Escribe una instrucción y haz clic en{' '}
              <span className="mx-1 font-semibold text-neutral-300">
                “Previsualizar”
              </span>{' '}
              para ver el resultado aquí.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
