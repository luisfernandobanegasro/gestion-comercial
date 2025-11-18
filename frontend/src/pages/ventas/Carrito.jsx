// src/pages/ventas/Carrito.jsx
import { Trash2 } from 'lucide-react';

export default function Carrito({
  carrito = [],
  total = 0,
  cliente,
  isEditing,
  carritoRef,
  scrollToCarrito,   // por si lo usas en otros lados
  guardarVenta,
  setCant,
  inc,
  dec,
  quitar,
}) {
  const puedeCrearVenta = !!cliente && carrito.length > 0;
  const totalNumero = Number(total || 0);

  return (
    <>
      {/* Panel principal del carrito */}
      <div ref={carritoRef} className="card carrito-card">
        <h3 style={{ marginBottom: 8 }}>Carrito ({carrito.length})</h3>

        <div style={{ overflowX: 'auto' }}>
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: 13,
            }}
          >
            <thead>
              <tr style={{ color: 'var(--muted)' }}>
                <th style={{ textAlign: 'left', padding: '4px 8px', width: '45%' }}>
                  Prod.
                </th>
                <th
                  className="col-cant"
                  style={{
                    textAlign: 'center',
                    padding: '4px 4px',
                    width: '25%',
                    whiteSpace: 'nowrap',
                  }}
                >
                  Cant.
                </th>
                <th
                  style={{
                    textAlign: 'right',
                    padding: '4px 4px',
                    whiteSpace: 'nowrap',
                  }}
                >
                  PU
                </th>
                <th
                  style={{
                    textAlign: 'right',
                    padding: '4px 4px',
                    whiteSpace: 'nowrap',
                  }}
                >
                  Subto.
                </th>
                <th style={{ width: 32 }} />
              </tr>
            </thead>
            <tbody>
              {carrito.length === 0 && (
                <tr>
                  <td
                    colSpan={5}
                    style={{
                      padding: '10px 8px',
                      color: 'var(--muted)',
                      fontSize: 13,
                    }}
                  >
                    No hay productos en el carrito.
                  </td>
                </tr>
              )}

              {carrito.map((item, i) => {
                const precioUnit = Number(item.precio_unit || 0);
                const subtotal = precioUnit * Number(item.cantidad || 0);

                return (
                  <tr key={i} style={{ borderTop: '1px solid var(--border)' }}>
                    {/* Nombre producto */}
                    <td style={{ padding: '6px 8px', verticalAlign: 'middle' }}>
                      <div
                        style={{
                          fontSize: 13,
                          fontWeight: 500,
                          whiteSpace: 'nowrap',
                          textOverflow: 'ellipsis',
                          overflow: 'hidden',
                          maxWidth: 150,
                        }}
                        title={item.nombre}
                      >
                        {item.nombre}
                      </div>
                    </td>

                    {/* Cantidad con stepper */}
                    <td
                      className="col-cant"
                      style={{
                        padding: '6px 4px',
                        verticalAlign: 'middle',
                        textAlign: 'center',
                      }}
                    >
                      <div className="qty-stepper">
                        <button
                          type="button"
                          className="btn-icon"
                          onClick={() => dec(i)}
                          aria-label="Disminuir cantidad"
                        >
                          –
                        </button>
                        <input
                          className="input-cantidad"
                          type="number"
                          min={1}
                          value={item.cantidad}
                          onChange={e => setCant(i, e.target.value)}
                        />
                        <button
                          type="button"
                          className="btn-icon"
                          onClick={() => inc(i)}
                          aria-label="Aumentar cantidad"
                        >
                          +
                        </button>
                      </div>
                    </td>

                    {/* Precio unitario */}
                    <td
                      style={{
                        padding: '6px 4px',
                        verticalAlign: 'middle',
                        textAlign: 'right',
                        fontVariantNumeric: 'tabular-nums',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      Bs. {precioUnit.toFixed(2)}
                    </td>

                    {/* Subtotal */}
                    <td
                      style={{
                        padding: '6px 4px',
                        verticalAlign: 'middle',
                        textAlign: 'right',
                        fontVariantNumeric: 'tabular-nums',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      Bs. {subtotal.toFixed(2)}
                    </td>

                    {/* Eliminar */}
                    <td
                      style={{
                        padding: '6px 4px',
                        textAlign: 'center',
                        verticalAlign: 'middle',
                      }}
                    >
                      <button
                        type="button"
                        onClick={() => quitar(i)}
                        style={{
                          border: 'none',
                          background: 'transparent',
                          padding: 4,
                          cursor: 'pointer',
                          color: 'var(--muted)',
                        }}
                        title="Quitar del carrito"
                      >
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Total y botón crear venta */}
        <div
          style={{
            borderTop: '1px solid var(--border)',
            marginTop: 8,
            paddingTop: 8,
          }}
        >
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 8,
            }}
          >
            <span style={{ color: 'var(--muted)', fontSize: 14 }}>Total:</span>
            <span
              style={{
                fontWeight: 700,
                fontSize: 16,
                fontVariantNumeric: 'tabular-nums',
                whiteSpace: 'nowrap',
              }}
            >
              Bs. {totalNumero.toFixed(2)}
            </span>
          </div>

          <button
            type="button"
            onClick={guardarVenta}
            disabled={!puedeCrearVenta}
            className="btn-primary"
            style={{ width: '100%' }}
          >
            {isEditing ? 'Guardar cambios' : 'Crear Venta'}
          </button>
          {!cliente && (
            <p
              style={{
                marginTop: 6,
                fontSize: 12,
                color: 'var(--muted)',
              }}
            >
              Selecciona un cliente para habilitar la venta.
            </p>
          )}
        </div>
      </div>

      {/* CTA flotante para móvil (opcional, usa el mismo total) */}
      <div className="venta-cta">
        <div className="cta-left">
          <span style={{ fontSize: 12, color: 'var(--muted)' }}>Total</span>
          <strong
            style={{
              fontSize: 14,
              fontVariantNumeric: 'tabular-nums',
              whiteSpace: 'nowrap',
            }}
          >
            Bs. {totalNumero.toFixed(2)}
          </strong>
        </div>
        <div className="cta-actions">
          <button
            type="button"
            className="btn-secondary"
            onClick={scrollToCarrito}
          >
            Ver carrito
          </button>
          <button
            type="button"
            className="btn-primary"
            disabled={!puedeCrearVenta}
            onClick={guardarVenta}
          >
            {isEditing ? 'Guardar' : 'Crear venta'}
          </button>
        </div>
      </div>

      {/* Estilos específicos del carrito */}
      <style>{`
        .carrito-card td.col-cant {
          overflow: visible;
          white-space: nowrap;
          text-overflow: initial;
        }

        .qty-stepper {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          border: 1px solid var(--border);
          border-radius: 999px;
          padding: 2px;
          background: rgba(15,23,42,0.75);
        }
        .qty-stepper .btn-icon {
          border: none;
          width: 26px;
          height: 26px;
          border-radius: 999px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: transparent;
          color: var(--text);
          cursor: pointer;
          font-size: 16px;
          line-height: 1;
        }
        .qty-stepper .btn-icon:hover {
          background: rgba(148,163,184,0.2);
        }
        .qty-stepper .input-cantidad {
          width: 42px;
          height: 24px;
          border: none;
          text-align: center;
          background: transparent;
          color: var(--text);
          font-weight: 600;
          font-variant-numeric: tabular-nums;
          padding: 0 4px;
          font-size: 13px;
        }
        .qty-stepper .input-cantidad:focus {
          outline: none;
        }
        .qty-stepper .input-cantidad::-webkit-outer-spin-button,
        .qty-stepper .input-cantidad::-webkit-inner-spin-button {
          -webkit-appearance: none;
          margin: 0;
        }
        .qty-stepper .input-cantidad[type="number"] {
          -moz-appearance: textfield;
          appearance: textfield;
        }

        /* CTA móvil pegado abajo de la pantalla */
        .venta-cta {
          position: fixed;
          left: 0;
          right: 0;
          bottom: 0;
          display: flex;
          gap: 12px;
          align-items: center;
          justify-content: space-between;
          padding: 10px 14px;
          background: var(--surface);
          border-top: 1px solid var(--border);
          z-index: 50;
          box-shadow: 0 -6px 24px rgba(0,0,0,.25);
        }
        .venta-cta .cta-left {
          display: flex;
          flex-direction: column;
        }
        .venta-cta .cta-actions {
          display: flex;
          gap: 8px;
        }
        @media (min-width: 1025px) {
          .venta-cta {
            display: none;
          }
        }
      `}</style>
    </>
  );
}
