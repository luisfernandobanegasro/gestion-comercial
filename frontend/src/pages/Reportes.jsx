import { useState } from 'react'
import api from '../api/axios'
import { PATHS } from '../api/paths'

export default function Reportes(){
  const [prompt, setPrompt] = useState('')
  const [reporte, setReporte] = useState('')
  const [busy, setBusy] = useState(false)

  const generar = async ()=>{
    if(!prompt.trim()) return
    setBusy(true); setReporte('')
    try{
      const { data } = await api.post(PATHS.reportes, { prompt })
      setReporte(typeof data === 'string' ? data : JSON.stringify(data, null, 2))
    }catch{
      setReporte('No se pudo generar el reporte.')
    }finally{ setBusy(false) }
  }

  return (
    <div className="grid">
      <div className="card">
        <h3>Generación dinámica de reportes (texto/voz)</h3>
        <div className="btn-row" style={{marginTop:8}}>
          <input style={{flex:'1 1 280px'}} placeholder="Ej: ventas de septiembre agrupadas por producto" value={prompt} onChange={e=>setPrompt(e.target.value)}/>
          <button className="primary" onClick={generar} disabled={busy}>{busy? 'Generando…':'Generar'}</button>
        </div>
      </div>
      {reporte && (
        <div className="card">
          <h3>Resultado</h3>
          <pre style={{whiteSpace:'pre-wrap', margin:0}}>{reporte}</pre>
        </div>
      )}
    </div>
  )
}
