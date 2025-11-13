// =============================
// PromptReport.jsx (mejorado)
// =============================
import { useRef, useState, useMemo, useEffect } from "react";
import api from "../../api/axios";
import { PATHS } from "../../api/paths";
import { Mic, StopCircle, Eye, Download, Loader2, Sparkles } from "lucide-react";

const includesPdf = (s) => /\bpdf\b/i.test(s || "");
const includesExcel = (s) => /\bexcel\b|\bxlsx\b/i.test(s || "");

export default function PromptReport(){
  const [text, setText] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [format, setFormat] = useState("auto");     // auto | pantalla | pdf | excel
  const [forcePreview, setForcePreview] = useState(false);
  const recRef = useRef(null);

  // --- Auto: si termina la voz, previsualiza ---
  useEffect(()=>{
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if(!SR) return;
    const rec = new SR();
    rec.lang = "es-ES";
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    rec.onresult = async (e) => {
      const t = e.results?.[0]?.[0]?.transcript || "";
      if(t){
        setText(t);
        // previsualización automática
        const p = t.replace(/\b(pdf|excel|xlsx)\b/gi, "").trim();
        if(p){
          setLoading(true);
          try{
            const res = await api.post(PATHS.reportes, { prompt: p });
            setData(res.data);
          }catch(err){
            console.error(err);
          }finally{ setLoading(false); }
        }
      }
      setListening(false);
    };
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);
    recRef.current = rec;
  },[]);

  const speakStart = () => {
    if(!recRef.current){ alert("Tu navegador no soporta reconocimiento de voz."); return; }
    setData(null);
    recRef.current.start();
    setListening(true);
  };
  const speakStop = () => { recRef.current?.stop(); setListening(false); };

  // prompt que usaremos para DESCARGA (si no forzamos preview)
  const downloadPrompt = useMemo(() => {
    const raw = (text || "").trim();
    if (!raw) return "";

    if (forcePreview) return raw.replace(/\b(pdf|excel|xlsx)\b/gi, "").trim();

    if (includesPdf(raw) || includesExcel(raw)) return raw; // ya lo dijo

    if (format === "pdf")   return raw + " en pdf";
    if (format === "excel") return raw + " en excel";
    return raw; // auto
  }, [text, format, forcePreview]);

  const preview = async () => {
    const base = (text || "").trim();
    if(!base) return;
    const p = (forcePreview || format === "pantalla")
      ? base.replace(/\b(pdf|excel|xlsx)\b/gi, "")
      : base.replace(/\b(pdf|excel|xlsx)\b/gi, ""); // siempre limpio para preview
    setLoading(true);
    try{
      const res = await api.post(PATHS.reportes, { prompt: p.trim() });
      setData(res.data);
    }finally{ setLoading(false); }
  };

  const download = async () => {
    if (forcePreview) return; // bloqueado con toggle
    const p = downloadPrompt;
    if(!p) return;
    if (format === "auto" && !includesPdf(p) && !includesExcel(p)){
      alert("Indica el formato (PDF o Excel) en el selector o en el prompt.");
      return;
    }
    setLoading(true);
    try{
      const res = await api.post(PATHS.reportes, { prompt: p }, { responseType: "blob" });
      const cd = res.headers["content-disposition"] || "";
      const match = cd.match(/filename="(.+?)"/i);
      const filename = match ? match[1] : (includesPdf(p) ? "reporte.pdf" : includesExcel(p) ? "reporte.xlsx" : "reporte.bin");
      const url = URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url; a.download = filename; a.click();
      URL.revokeObjectURL(url);
    }finally{ setLoading(false); }
  };

  const cols = data?.headers || [];
  const rows = data?.rows || [];

  return (
    <div className="max-w-6xl mx-auto p-4">
      <div className="bg-neutral-900/40 border border-neutral-800 rounded-2xl p-4 md:p-6 shadow-lg">
        <div className="flex items-center gap-2 mb-3 text-neutral-300">
          <Sparkles size={18} className="text-cyan-400"/>
          <h2 className="text-lg md:text-xl font-semibold">Generador de Reportes</h2>
        </div>

        <textarea
          className="w-full min-h-[110px] md:min-h-[120px] rounded-xl bg-neutral-950 border border-neutral-800 focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 text-neutral-200 p-3 md:p-4 outline-none placeholder:text-neutral-500"
          placeholder={`Ejemplos:\n• "Quiero un reporte de ventas del mes pasado por cliente en PDF"\n• "Top 5 productos por categoría este trimestre en Excel"`}
          value={text}
          onChange={(e)=>setText(e.target.value)}
        />

        <div className="mt-3 flex flex-col sm:flex-row gap-2 sm:items-center">
          <div className="flex gap-2">
            {!listening ? (
              <button onClick={speakStart} className="inline-flex items-center gap-2 px-3 py-2 rounded-xl border border-neutral-800 bg-neutral-950 hover:bg-neutral-900 text-neutral-200">
                <Mic size={18}/> Dictar
              </button>
            ) : (
              <button onClick={speakStop} className="inline-flex items-center gap-2 px-3 py-2 rounded-xl border border-neutral-800 bg-red-600/10 hover:bg-red-600/20 text-red-300">
                <StopCircle size={18}/> Detener
              </button>
            )}

            <select
              className="px-3 py-2 rounded-xl border border-neutral-800 bg-neutral-950 text-neutral-200"
              value={format}
              onChange={(e)=>setFormat(e.target.value)}
              disabled={loading || forcePreview}
              title={forcePreview ? "Desactivado: Forzar previsualización está activo" : "Formato preferido"}
            >
              <option value="auto">Auto</option>
              <option value="pantalla">Pantalla</option>
              <option value="pdf">PDF</option>
              <option value="excel">Excel</option>
            </select>

            <label className="inline-flex items-center gap-2 px-3 py-2 rounded-xl border border-neutral-800 bg-neutral-950 text-neutral-200">
              <input type="checkbox" className="accent-cyan-500" checked={forcePreview} onChange={(e)=>setForcePreview(e.target.checked)} />
              Forzar previsualización
            </label>
          </div>

          <div className="flex gap-2 sm:ml-auto">
            <button onClick={preview} disabled={loading} className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-neutral-800 bg-neutral-950 hover:bg-neutral-900 text-neutral-200">
              {loading ? <Loader2 className="animate-spin" size={18}/> : <Eye size={18}/>} Previsualizar
            </button>
            <button onClick={download} disabled={loading || forcePreview} title={forcePreview ? "Desactivado por Forzar previsualización" : "Descargar"} className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-500 text-neutral-900 font-medium hover:bg-cyan-400 ${forcePreview?"opacity-60 cursor-not-allowed":""}`}>
              {loading ? <Loader2 className="animate-spin" size={18}/> : <Download size={18}/>} Descargar
            </button>
          </div>
        </div>
      </div>

      {/* Tabla */}
      {data && (
        <div className="mt-6 bg-neutral-900/40 border border-neutral-800 rounded-2xl p-3 md:p-4 shadow-lg">
          <h3 className="text-neutral-300 font-medium mb-3">Previsualización</h3>
          <div className="overflow-x-auto">
            <table className="min-w-[760px] w-full text-sm">
              <thead>
                <tr className="text-neutral-400">
                  {cols.map((h)=> (
                    <th key={h} className="text-left px-3 py-2 border-b border-neutral-800 bg-neutral-950 sticky top-0">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.length>0 ? rows.map((r,i)=> (
                  <tr key={i} className="odd:bg-neutral-950/30">
                    {r.map((c,j)=> (
                      <td key={j} className={`px-3 py-2 ${/monto|total|cantidad/i.test(cols[j]||"")?"text-right": ""}`}>{c}</td>
                    ))}
                  </tr>
                )) : (
                  <tr><td className="px-3 py-6 text-neutral-400" colSpan={cols.length||1}>Sin resultados</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

