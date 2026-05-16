# Ecdótica Gramática — Checklist operativo de setup

Pasos concretos para crear el programa en ecdotica.com. La mayor parte se hace en **wp-admin**, no en este repo.

Ver también: [`programa-gramatica-plan.md`](./programa-gramatica-plan.md) para el plan completo.

---

## Día 1 — Preparación (1 hora)

1. **Backup completo** desde el panel de EasyWP → `Backup → Generate Now`. Sin esto, no tocar nada.
2. **Staging site** en EasyWP → `Create Staging`. Trabajar ahí hasta el día 4.
3. **Verificar Stripe.** `WooCommerce → Settings → Payments → Stripe`. Confirmar que está conectado y que tiene activado **"Accept recurring payments"**.

---

## Día 2 — Comprar e instalar plugins (2 horas)

En este orden exacto:

1. **WooCommerce Subscriptions** — comprar en woocommerce.com/products/woocommerce-subscriptions, descargar `.zip`, subir vía `Plugins → Add New → Upload`. **$239/año.**
2. **WooCommerce Memberships** — mismo proceso. **$199/año.**
3. **Tutor LMS** (gratis) — desde `Plugins → Add New`, buscar "Tutor LMS". Activar.
4. **Tutor LMS Pro** — comprar en themeum.com/tutor-lms, descargar `.zip`, subir. **$199/año.**

Verificación: deben aparecer los menús `Tutor LMS`, `WooCommerce → Subscriptions`, `WooCommerce → Memberships`.

---

## Día 3 — Configuración base (2 horas)

### Tutor LMS → Settings

- `Monetization`: activar **WooCommerce** (no usar el "Native" que viene por defecto).
- `Course → Content Drip`: marcar **Enable Content Drip**, modo "Available after X days from enrollment".
- `Advanced → Course Permalink Base`: `gramatica` (URLs limpias: `ecdotica.com/gramatica/nivel-1`).

### WooCommerce → Settings → Subscriptions

- Permitir cliente cambiar/cancelar suscripción desde "Mi cuenta".
- "Days before renewal email": **3 días**.

### Crear los 4 cursos vacíos

En `Tutor LMS → Courses → Add New`:
- `Nivel 1 — Fundamentos`
- `Nivel 2 — Estructura`
- `Nivel 3 — Norma y estilo`
- `Nivel 4 — Escritura avanzada`

Sin lecciones todavía. Solo título, descripción corta y portada placeholder.

### Crear el producto de suscripción

En `Products → Add New`:
- Nombre: `Suscripción Ecdótica Gramática`
- Tipo (dropdown debajo del precio): **Simple subscription**
- Precio: `7.99`, cada `1 month`, "Expire after": `Never`
- Sign-up fee: `0`
- **Free trial: `7 days`**
- Marcar **Virtual**

---

## Día 4 — Conectar acceso y probar (2 horas)

### Crear el plan de membresía

En `WooCommerce → Memberships → Membership Plans → Add New`:
- Nombre: `Alumno Ecdótica Gramática`
- Grant access via: **purchase** → seleccionar el producto creado el día 3
- Tab `Restrict Content`: agregar regla "Course" → seleccionar los 4 cursos
- Tab `Members Area`: marcar **Auto-enroll into courses**

### Test end-to-end

1. Cerrar sesión. Ir a `/gramatica`. Comprar con tarjeta de prueba Stripe: `4242 4242 4242 4242`, fecha futura, CVC `123`.
2. **Verificar:** no se cobra, la suscripción aparece en estado "Active", la membresía aparece en "Mi cuenta", y Nivel 1 está visible.
3. **Forzar avance del drip:** en `Tutor LMS → Enrollments`, editar el enrollment y mover la fecha 30 días hacia atrás. Recargar el curso → Nivel 2 debe desbloquearse.
4. **Cancelar suscripción** desde "Mi cuenta" → confirmar que el acceso sigue activo hasta el fin del período pagado (no se revoca al instante).

Si esos 4 pasos pasan, la infraestructura está lista. Si algo falla, **no avanzar** a producción de contenido: arreglar primero.

---

## Semana 2 en adelante — Contenido en Bunny Stream

1. Crear cuenta en bunny.net → activar **Stream** (no Storage; es otro producto).
2. Crear Video Library `ecdotica-gramatica`.
3. Habilitar **DRM básico** y **token authentication** (evita copia del embed).
4. Para cada lección: subir video → copiar el embed iframe → pegar en el editor de la lección de Tutor LMS como bloque HTML.

**Grabación:** OBS Studio (gratis) o Loom Business ($15/mes). Cámara opcional; lo importante es audio limpio. Un Lavalier USB de ~$30 alcanza.

---

## Registro de IDs en producción

Llenar esta tabla **después** del Día 4 con los IDs reales del sitio en producción. Son frágiles: si EasyWP migra el sitio o se reinstala un plugin, pueden romperse.

| Recurso | ID en producción | Notas |
|---|---|---|
| Producto suscripción mensual | _pendiente_ | $7.99/mes |
| Producto suscripción anual | _pendiente_ | $71/año |
| Membership plan "Alumno Ecdótica Gramática" | _pendiente_ | — |
| Curso Nivel 1 | _pendiente_ | — |
| Curso Nivel 2 | _pendiente_ | Drip día 28 |
| Curso Nivel 3 | _pendiente_ | Drip día 56 |
| Curso Nivel 4 | _pendiente_ | Drip día 98, cap 20 |
| Certificado Nivel 1 | _pendiente_ | — |
| Bunny Stream Library | _pendiente_ | `ecdotica-gramatica` |

---

## Credenciales / variables (no commitear valores)

Estas viven en wp-admin o como secrets, **nunca** en este repo:

| Variable | Dónde | Para qué |
|---|---|---|
| Stripe Live Key | WooCommerce → Stripe settings | Cobro recurrente |
| Stripe Webhook Secret | WooCommerce → Stripe settings | Verificación de eventos |
| Bunny Stream API Key | Bunny dashboard | Subida programática de video (opcional) |
| Bunny Stream Library ID | Bunny dashboard | Embed iframes |
| SMTP credentials (`gramatica@ecdotica.com`) | WP Mail SMTP / similar | Emails transaccionales |

---

## Snippets PHP versionables (a futuro)

Cuando se necesite personalizar Tutor LMS (certificado, emails, hooks), versionar los snippets aquí:

```
wordpress-plugin/tutor-lms-customizations/
├── certificate-customization.php
├── email-templates/
└── hooks.php
```

Pegar el código tal cual está en el `functions.php` del tema o en un plugin "Code Snippets". No modificar el core de Tutor LMS Pro: los cambios se pierden al actualizar.
