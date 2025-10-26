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
        <div>
          <Elements options={{ clientSecret }} stripe={stripePromise}>
            <StripeCheckoutForm venta={venta} onPaymentSuccess={onPaymentSuccess} />
          </Elements>
          <button onClick={() => { setActiveView('options'); setClientSecret(''); }} style={{marginTop: '8px'}}>Cancelar Pago con Tarjeta</button>
        </div>
      )}

      {activeView === 'qr' && (
        <div style={{ textAlign: 'center' }}>
          <h4>Pagar Bs. {venta.total}</h4>
          <div style={{ background: 'white', padding: '16px', display: 'inline-block', margin: '16px 0' }}>
            <QRCode value={qrData} size={200} />
          </div>
          {config && (
            <div style={{ textAlign: 'left', background: 'var(--bg-alt, var(--bg))', padding: '12px', borderRadius: '8px' }}>
              <p>O transfiere a:</p>
              <p><strong>Banco:</strong> {config.nombre_banco}<br/><strong>Cuenta:</strong> {config.numero_cuenta}<br/><strong>Titular:</strong> {config.nombre_titular}</p>
            </div>
          )}
          <button className="primary" onClick={registrarPagoEfectivo} style={{marginTop: '16px'}}>He realizado el pago</button>
          <button onClick={() => setActiveView('options')} style={{marginTop: '8px'}}>Cancelar Pago con QR</button>
        </div>
      )}
    </>
  )
}