
export const PATHS = {
  auth: {
    login: '/cuentas/token/',
    refresh: '/cuentas/token/refresh/',
    me: '/cuentas/yo/',
    register: '/cuentas/usuarios/',                 // POST: {username,email,password}
    passwordResetRequest: '/cuentas/password/reset/',       // POST: {email}
    passwordResetConfirm: '/cuentas/password/reset/confirm/'// POST: {uid, token, new_password}

  },
  usuarios: '/cuentas/usuarios/',
  roles: '/cuentas/roles/',
  permisos: '/cuentas/permisos/',
  productos: '/catalogo/productos/',
  categorias: '/catalogo/categorias/',
  marcas: '/catalogo/marcas/',
  clientes: '/clientes/',
  ventas: {
    root: '/ventas/ventas/',
    confirmar: (id)=> `/ventas/ventas/${id}/confirmar_pago/`,
    comprobante: (id) => `/ventas/ventas/${id}/comprobante/`,
  },
  pagos: {
    stripeIntent: '/pagos/stripe/intent/',
    stripeConfirmar: '/pagos/stripe/confirmar/',
    stripeReembolsar: '/pagos/stripe/reembolsar/',
  },
  auditoria: '/auditoria/', // Corregido: apunta a la nueva ruta raíz
  reportes: '/reportes/prompt/',
  configuracion: '/configuracion/', // <-- Añadido
}
