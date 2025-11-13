import { useState, useEffect, useRef } from 'react';
import api from '../../api/axios.js';
import { Mic, StopCircle, Download, Eye, Loader2 } from 'lucide-react';

export default function Reportes(){
  const [prompt, setPrompt] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [previewData, setPreviewData] = useState(null);

  const recRef = useRef(null);

  useEffect(()=>{
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return;

    const recognition = new SR();
    recognition.continuous = false;
    recognition.lang = 'es-ES';
    recognition.interimResults = false;

    recognition.onresult = async (evt)=>{
      const t = evt.results?.[0]?.[0]?.transcript || '';
      setPrompt(t);
      // Auto-previsualizar
      try{
        setIsLoading(true); setError(null); setPreviewData(null); setSuccessMessage(null);
        const clean = t.replace(/\b(en\s+)?(pdf|excel|xlsx)\b/gi, '').trim();
        if(clean){
          const r = await api.post('reportes/prompt/', { prompt: clean });
          setPreviewData(r.data);
        }
      }catch(err){ setError(err?.response?.data?.error||'No pude previsualizar'); }
      finally{ setIsLoading(false); setIsListening(false); }
    };
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);
    recRef.current = recognition;
  }, []);

  const handleListen = () => {
    if(!recRef.current){ alert('El reconocimiento de voz no es compatible.'); return; }
    setPreviewData(null); setError(null); setSuccessMessage(null);
    recRef.current.start(); setIsListening(true);
  };
  const stopListen = ()=>{ try{ recRef.current?.stop(); }catch{} setIsListening(false); };

  useEffect(() => {
    if (error || successMessage) {
      const timer = setTimeout(() => { setError(null); setSuccessMessage(null); }, 4500);
      return () => clearTimeout(timer);
    }
  }, [error, successMessage]);

  const handlePreview = async (e) => {
    e?.preventDefault?.();
    if (!prompt.trim()) return;
    setIsLoading(true); setError(null); setPreviewData(null); setSuccessMessage(null);
    try {
      const previewPrompt = prompt.replace(/\b(en\s+)?(pdf|excel|xlsx)\b/gi, '').trim();
      const response = await api.post('reportes/prompt/', { prompt: previewPrompt });
      setPreviewData(response.data);
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.detail || 'Ocurrió un error al previsualizar.');
    } finally { setIsLoading(false); }
  };

  const handleDownload = async (e) => {
    e?.preventDefault?.();
    if (!prompt.trim()) return;
    if (!/pdf|excel|xlsx/i.test(prompt)) { setError("Para descargar, especifica 'en PDF' o 'en Excel'."); return; }
    setIsLoading(true); setError(null); setPreviewData(null); setSuccessMessage(null);
    try {
      const response = await api.post('reportes/prompt/', { prompt }, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      const ext = /pdf/i.test(prompt) ? 'pdf' : 'xlsx';
      const filename = `reporte-${new Date().toISOString().slice(0,10)}.${ext}`;
      link.href = url; link.setAttribute('download', filename); document.body.appendChild(link); link.click(); link.remove();
      window.URL.revokeObjectURL(url);
      setSuccessMessage(`¡Reporte "${filename}" descargado con éxito!`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ocurrió un error al descargar el archivo.');
    } finally { setIsLoading(false); }
  };

  return (
    <div className="max-w-6xl mx-auto p-4">
      <div className="bg-neutral-900/40 border border-neutral-800 rounded-2xl p-4 md:p-6 shadow-lg">
        <h2 className="text-lg md:text-xl font-semibold text-neutral-200 mb-3">Generador de Reportes</h2>
        <div className="flex gap-2">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ej: Reporte de ventas de este mes agrupado por cliente en PDF..."
            disabled={isLoading}
            rows={3}
            className="flex-1 rounded-xl bg-neutral-950 border border-neutral-800 focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 text-neutral-200 p-3 outline-none placeholder:text-neutral-500"
          />
          {!isListening ? (
            <button onClick={handleListen} disabled={isLoading} className={`h-[46px] aspect-square grid place-items-center rounded-xl border border-neutral-800 ${isLoading?'opacity-60 cursor-not-allowed':'hover:bg-neutral-900'} bg-neutral-950 text-neutral-200`}>
              <Mic size={18} />
            </button>
          ) : (
            <button onClick={stopListen} className="h-[46px] aspect-square grid place-items-center rounded-xl border border-neutral-800 bg-red-600/10 hover:bg-red-600/20 text-red-300">
              <StopCircle size={18} />
            </button>
          )}
        </div>
        <div className="mt-3 flex gap-2">
          <button onClick={handlePreview} disabled={isLoading || !prompt.trim()} className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-neutral-800 bg-neutral-950 hover:bg-neutral-900 text-neutral-200">
            {isLoading ? <Loader2 className="animate-spin" size={18}/> : <Eye size={18}/>} Previsualizar
          </button>
          <button onClick={handleDownload} disabled={isLoading || !prompt.trim()} className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-500 text-neutral-900 font-medium hover:bg-cyan-400">
            {isLoading ? <Loader2 className="animate-spin" size={18}/> : <Download size={18}/>} Descargar
          </button>
        </div>
        {error && <div className="mt-4 text-red-300 bg-red-600/10 border border-red-900/40 rounded-xl p-3">{error}</div>}
        {successMessage && <div className="mt-4 text-emerald-300 bg-emerald-600/10 border border-emerald-900/40 rounded-xl p-3">{successMessage}</div>}
      </div>

      {previewData && (
        <div className="mt-6 bg-neutral-900/40 border border-neutral-800 rounded-2xl p-3 md:p-4 shadow-lg">
          <h3 className="text-neutral-300 font-medium mb-3">Previsualización del Reporte</h3>
          <div className="overflow-x-auto">
            <table className="min-w-[760px] w-full text-sm">
              <thead>
                <tr className="text-neutral-400">
                  {(previewData.headers||[]).map((h)=> <th key={h} className="text-left px-3 py-2 border-b border-neutral-800 bg-neutral-950 sticky top-0">{h}</th>)}
                </tr>
              </thead>
              <tbody>
                {(previewData.rows?.length>0) ? (
                  previewData.rows.map((row,i)=> (
                    <tr key={i} className="odd:bg-neutral-950/30">
                      {row.map((cell,j)=> <td key={j} className={`px-3 py-2 ${/monto|total|cantidad/i.test((previewData.headers||[])[j]||'')?'text-right':''}`}>{cell}</td>)}
                    </tr>
                  ))
                ) : (
                  <tr><td className="px-3 py-6 text-neutral-400" colSpan={(previewData.headers||[]).length||1}>No se encontraron resultados.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
