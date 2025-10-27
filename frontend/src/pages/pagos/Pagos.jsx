import { useState, useEffect } from 'react'
import { loadStripe } from '@stripe/stripe-js'
import { Elements } from '@stripe/react-stripe-js'
import { QRCodeSVG as QRCode } from 'qrcode.react'
import api from '../../api/axios'
import { PATHS } from '../../api/paths'
import StripeCheckoutForm from './StripeCheckoutForm'

// Carga tu clave pública de Stripe desde las variables de entorno
const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY);

export default function Pagos({ venta, onPaymentSuccess }) {
  const [clientSecret, setClientSecret] = useState('');
  const [config, setConfig] = useState(null);
  // Usamos un solo estado para controlar la vista activa, lo que es más limpio y seguro.
  const [isLoading, setIsLoading] = useState(false);
  const [activeView, setActiveView] = useState('options'); // 'options', 'stripe', 'qr'

  useEffect(() => {
    // Cargar la configuración del sistema para mostrarla en el pago QR
    if (activeView === 'qr' && !config) {
      api.get(PATHS.configuracion).then(res => setConfig(res.data)).catch(() => {});
    }
  }, [activeView, config]);

  const registrarPagoEfectivo = async () => {
    if (!window.confirm("¿Confirmar que se ha recibido el pago en efectivo? Esta acción descontará el stock.")) return
    try {
      // El endpoint de confirmar se encarga de todo en el backend
      await api.post(PATHS.ventas.confirmar(venta.id))
      alert("Pago en efectivo registrado. La venta ha sido marcada como 'Pagada'.")
      onPaymentSuccess() // Notificar al componente padre que el pago fue exitoso
    } catch (error) {
      console.error("Error al registrar pago en efectivo:", error)
      alert(`Error: ${error.response?.data?.detail || 'No se pudo registrar el pago.'}`)
    }
  }

  const iniciarPagoStripe = async () => {
    setIsLoading(true);
    try {
      // Llama al backend para crear un PaymentIntent y obtener el clientSecret
      const response = await api.post(PATHS.pagos.stripeIntent, { venta_id: venta.id });
      setClientSecret(response.data.clientSecret);
      setActiveView('stripe'); // <-- Solo cambiamos la vista si todo fue bien
    } catch (error) {
      console.error("Error al crear el intento de pago:", error);
      alert("No se pudo iniciar el proceso de pago. Inténtalo de nuevo.");
    }
    setIsLoading(false);
  }

  // Generar datos para el QR dinámico
  const qrData = JSON.stringify({
    folio: venta.folio,
    monto: venta.total,
    moneda: "BOB",
    concepto: config?.glosa_qr || "Pago de productos"
  });

  return (
    <>
      <h3>Opciones de Pago</h3>

      {activeView === 'options' && (
        <div className="btn-row">
          <button className="primary" onClick={registrarPagoEfectivo}>Registrar Pago en Efectivo</button>
          <button onClick={iniciarPagoStripe} disabled={isLoading}>{isLoading ? 'Iniciando...' : 'Pagar con Tarjeta'}</button>
          <button onClick={() => setActiveView('qr')}>Pagar con QR</button>
        </div>
      )}

      {/* Solo renderizamos el componente de Stripe si la vista es 'stripe' Y tenemos un clientSecret */}
      {activeView === 'stripe' && clientSecret && (
        <div className="pay-panel">
          <Elements options={{ clientSecret, appearance:{ theme: 'night' } }} stripe={stripePromise}>
            <StripeCheckoutForm venta={venta} onPaymentSuccess={onPaymentSuccess} />
          </Elements>
          <button onClick={() => { setActiveView('options'); setClientSecret(''); }} className="ghost mt-8">
            Cancelar Pago con Tarjeta
          </button>
        </div>
      )}


      {activeView === 'qr' && (
        <div className="qr-wrap">
          <div className="qr-left">
            <h4 className="amount">Pagar Bs. {Number(venta.total).toFixed(2)}</h4>
            <div className="qr-box">
              <QRCode value={qrData} size={220} />
            </div>
            <div className="btn-row">
              <button className="primary" onClick={registrarPagoEfectivo}>He realizado el pago</button>
              <button className="ghost" onClick={() => setActiveView('options')}>Cancelar</button>
            </div>
          </div>

          <div className="qr-right">
            <div className="bank-info">
              <h5>Transferencia alternativa</h5>
              {config ? (
                <ul>
                  <li><strong>Banco:</strong> {config.nombre_banco}</li>
                  <li><strong>Cuenta:</strong> {config.numero_cuenta}</li>
                  <li><strong>Titular:</strong> {config.nombre_titular}</li>
                  {config.documento_titular && <li><strong>Documento:</strong> {config.documento_titular}</li>}
                </ul>
              ) : <p className="muted">Cargando datos de cuenta…</p>}
            </div>
            <p className="muted xs">Escanea el QR con tu app bancaria. Concepto: {config?.glosa_qr || 'Pago de productos'}.</p>
          </div>
        </div>
      )}

    </>
  )
}