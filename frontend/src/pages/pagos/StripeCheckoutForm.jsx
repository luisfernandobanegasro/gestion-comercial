import { useState } from 'react';
import { useStripe, useElements, PaymentElement } from '@stripe/react-stripe-js';
import api from '../../api/axios';
import { PATHS } from '../../api/paths';

export default function StripeCheckoutForm({ venta, onPaymentSuccess }) {
  const stripe = useStripe();
  const elements = useElements();

  const [errorMessage, setErrorMessage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) {
      // Stripe.js has not yet loaded.
      return;
    }

    setIsProcessing(true);

    // 1. Confirma el pago en el lado del cliente con Stripe
    const { error: stripeError, paymentIntent } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        // No necesitamos una return_url porque manejaremos el resultado aquí mismo
      },
      redirect: 'if_required' // Evita la redirección automática
    });

    if (stripeError) {
      setErrorMessage(stripeError.message);
      setIsProcessing(false);
      return;
    }

    // 2. Si el pago en Stripe fue exitoso (paymentIntent.status === 'succeeded'),
    //    notificamos a nuestro backend para que actualice el estado de la venta y el stock.
    if (paymentIntent.status === 'succeeded') {
      try {
        await api.post(PATHS.ventas.confirmar(venta.id));
        alert('¡Pago completado con éxito!');
        onPaymentSuccess();
      } catch (backendError) {
        setErrorMessage('El pago fue exitoso pero hubo un error al confirmar la venta en nuestro sistema. Por favor, contacta a soporte.');
      }
    } else {
      setErrorMessage('El pago no se completó. Estado: ' + paymentIntent.status);
    }

    setIsProcessing(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <PaymentElement />
      <button disabled={isProcessing || !stripe || !elements} className="primary" style={{ marginTop: '16px', width: '100%' }}>
        {isProcessing ? "Procesando..." : `Pagar Bs. ${venta.total}`}
      </button>
      {errorMessage && <div style={{ color: 'red', marginTop: '10px' }}>{errorMessage}</div>}
    </form>
  );
}