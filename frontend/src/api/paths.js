// src/api/paths.js

export const PATHS = {
  auth: {
    login: '/cuentas/token/',
    refresh: '/cuentas/token/refresh/',
    me: '/cuentas/yo/',
    register: '/cuentas/usuarios/',
    passwordResetRequest: '/cuentas/password/reset/',
    passwordResetConfirm: '/cuentas/password/reset/confirm/',
  },

  usuarios: '/cuentas/usuarios/',
  roles: '/cuentas/roles/',
  permisos: '/cuentas/permisos/',

  productos: '/catalogo/productos/',
  categorias: '/catalogo/categorias/',
  marcas: '/catalogo/marcas/',

  ofertas: {
    root: '/catalogo/ofertas/',
  },

  clientes: '/clientes/',

  ventas: {
    root: '/ventas/ventas/',
    confirmar: (id) => `/ventas/ventas/${id}/confirmar_pago/`,
    comprobante: (id) => `/ventas/ventas/${id}/comprobante/`,

    // 🛒 Endpoints de carrito
    carrito: '/ventas/ventas/carrito/',
    carritoItem: (itemId) => `/ventas/ventas/carrito/items/${itemId}/`,
    carritoConfirmar: '/ventas/ventas/carrito/confirmar/',
  },

  pagos: {
    stripeIntent: '/pagos/stripe/intent/',
    stripeConfirmar: '/pagos/stripe/confirmar/',
    stripeReembolsar: '/pagos/stripe/reembolsar/',
  },

  auditoria: '/auditoria/',
  reportes: '/reportes/prompt/',
  configuracion: '/configuracion/',
}
