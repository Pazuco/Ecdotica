# Programa de gramática en Ecdótica — Plan técnico de WordPress

**Sitio:** ecdotica.com
**Modelo:** Curso estructurado por niveles + suscripción mensual con WooCommerce
**Audiencia:** Estudiantes y público general hispanohablante
**Stack confirmado:** WordPress + WooCommerce + Stripe (ya en uso para el detector de plagio)
**Sub-marca:** Ecdótica Gramática (URL: `ecdotica.com/gramatica`)

---

## 1. Resumen ejecutivo

El programa se monta como un **LMS dentro de WordPress** acoplado a la infraestructura existente de WooCommerce + Stripe. La suscripción mensual otorga acceso a todo el catálogo de cursos de gramática, con **entrega progresiva** (content drip) para mantener al alumno comprometido mes a mes y reducir el churn.

**Pila recomendada (corta):**

- **Tutor LMS Pro** como motor de cursos
- **WooCommerce + WooCommerce Subscriptions** para cobro recurrente con Stripe
- **WooCommerce Memberships** como capa de control de acceso (gate único, evita conflictos)
- **Content drip nativo de Tutor LMS** para liberar lecciones por semana
- **Bunny Stream** como host de video (no YouTube ni Vimeo)

---

## 2. Decisiones tomadas

| # | Decisión | Detalle |
|---|---|---|
| 1 | **Precio** | $7.99/mes · variante anual $71/año (25% off) |
| 2 | **Hosting de video** | Bunny Stream (con DRM ligero + watermark dinámico por email) |
| 3 | **Tutor humano Nivel 4** | Lo asume Marcelo Paz Soldán; cap inicial de 20 alumnos simultáneos; SLA de feedback ≤ 10 días |
| 4 | **Bilingüe ES/EN** | Pospuesto a mes 6+; URLs y CPTs sin prefijos de idioma para no migrar después |
| 5 | **Marca** | "Ecdótica Gramática" como sub-marca; URL `/gramatica`; certificados emitidos a nombre de "Editorial Nuevo Milenio · Ecdótica Gramática"; emails desde `gramatica@ecdotica.com` |

---

## 3. Comparativa de plugins LMS (la decisión clave)

| Plugin | Precio anual | Suscripción mensual | Content drip | Quizzes/Certificados | Curva |
|---|---|---|---|---|---|
| **Tutor LMS Pro** ✓ | $199 todo incluido | Vía WooCommerce Subscriptions (addon nativo) | Sí, nativo Pro | Sí, ambos incluidos | Baja, UI moderna |
| LearnDash | $199 + addons ($49 c/u) | Vía WooCommerce Subscriptions | Sí, nativo | Sí, certificados con addon | Media-alta, más técnico |
| LifterLMS | Free core / bundle pago | Nativo + WooCommerce | Sí | Sí | Media |
| MasterStudy | Free / Pro $149 | Vía WooCommerce | Sí Pro | Sí | Baja |
| Sensei LMS | Free + WC Paid Courses | Sí, integración oficial con WC Memberships | Limitado | Sí | Baja, hecho por Automattic |

**Elegido: Tutor LMS Pro.** Razones:

1. UI moderna que un alumno general entiende sin ayuda — clave para público no técnico.
2. Addon nativo de WooCommerce Subscriptions — encaja directo con el Stripe ya configurado.
3. Precio fijo $199/año sin sorpresas de addons (LearnDash cobraría aparte certificados, reportes avanzados, etc.).
4. Marketplace multi-instructor disponible si más adelante se invitan profesores de literatura/edición.
5. Reseñas 2026 (SergiosKS, Mihael Cacic) lo posicionan como ideal para emprendedores y academias pequeñas-medianas.

Cuándo reconsiderar: si se proyectan más de 5.000 alumnos activos, integraciones corporativas pesadas o gamificación avanzada → migrar a LearnDash.

---

## 4. Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│  WordPress (ecdotica.com)                                   │
│                                                             │
│  ┌───────────────┐    ┌────────────────────┐                │
│  │  Tutor LMS    │◄──►│ WooCommerce        │                │
│  │  Pro          │    │ + Subscriptions    │                │
│  │               │    │ + Memberships      │                │
│  │  - Cursos     │    │ + Stripe Gateway   │                │
│  │  - Lecciones  │    └────────────────────┘                │
│  │  - Quizzes    │           │                              │
│  │  - Drip       │           ▼                              │
│  │  - Certif.    │    ┌────────────────────┐                │
│  └───────┬───────┘    │  Stripe (cobro     │                │
│          │            │  recurrente)       │                │
│          │            └────────────────────┘                │
│          ▼                                                  │
│  ┌────────────────────────────────────────┐                 │
│  │ Capa de acceso: WooCommerce Memberships│                 │
│  │ - Restringe cursos por plan            │                 │
│  │ - Auto-enroll al comprar suscripción   │                 │
│  └────────────────────────────────────────┘                 │
│                                                             │
│  Videos: Bunny Stream (iframe embed, fuera de WP)           │
└─────────────────────────────────────────────────────────────┘
```

**Punto crítico:** No vincular los cursos directamente a productos WooCommerce. Dejar que **Memberships** controle todo el acceso. Una sola capa de gating evita el escenario donde el LMS dice "tiene acceso" y Memberships dice "no".

---

## 5. Plugins a instalar (lista definitiva)

| # | Plugin | Costo año 1 | Función |
|---|---|---|---|
| 1 | WooCommerce | Gratis | Ya instalado |
| 2 | WooCommerce Subscriptions | $239 | Cobro recurrente mensual con Stripe |
| 3 | WooCommerce Memberships | $199 | Control de acceso unificado |
| 4 | Tutor LMS (free) | Gratis | Base del LMS |
| 5 | Tutor LMS Pro | $199 | Drip, certificados, quizzes avanzados, addon WC Subscriptions |
| 6 | Stripe Gateway para WooCommerce | Gratis | Ya instalado |
| ~~7~~ | ~~WPML/Polylang~~ | — | **Diferido al mes 6+** |

**Inversión inicial primer año en licencias: $637 USD.**
Renovaciones año 2+: usualmente 50% de descuento.

---

## 6. Estructura de cursos y niveles

Programa "Gramática del español para escribir mejor", organizado en **4 niveles**. Cada nivel = 1 curso en Tutor LMS.

### Nivel 1 — Fundamentos (4 semanas)
- Sustantivos, adjetivos, artículos
- Verbos: conjugación regular e irregular
- Concordancia básica
- Puntuación esencial (coma, punto, mayúsculas)

### Nivel 2 — Estructura (4 semanas)
- Oración simple y compuesta
- Sujeto, predicado y complementos
- Pronombres (leísmo, laísmo, loísmo)
- Acentuación: tildes diacríticas y casos especiales

### Nivel 3 — Norma y estilo (6 semanas)
- Verbos compuestos y perífrasis
- Subjuntivo y modo verbal
- Conectores y cohesión textual
- Ortotipografía (comillas, guiones, cursivas)
- Errores frecuentes de la RAE actual

### Nivel 4 — Escritura avanzada (6 semanas, con tutoría humana)
- Sintaxis para escritores
- Estilo directo, indirecto e indirecto libre
- Voz narrativa y registro
- Edición y corrección de textos propios
- **Taller final corregido por instructor (Marcelo)**
- Cap simultáneo: 20 alumnos · SLA: ≤ 10 días por feedback

**Total: 20 semanas (~5 meses)** de progresión guiada.

---

## 7. CPTs y taxonomías

Tutor LMS ya provee los CPTs necesarios — no construir propios:

| CPT (provisto por Tutor LMS) | Uso |
|---|---|
| `courses` | Cada nivel del programa |
| `lesson` | Unidad de teoría (vídeo + texto) |
| `tutor_quiz` | Ejercicios autocorregibles |
| `tutor_assignments` | Tareas con corrección manual (Nivel 4) |
| `tutor-certificate` | Certificado al completar nivel |

**Taxonomías personalizadas que sí conviene añadir:**
- `course-category`: Niveles, Específicos (RAE, ortotipografía, etc.)
- `course-tag`: Etiquetas finas: "tildes", "subjuntivo", "leísmo"…

---

## 8. Producto de suscripción WooCommerce

**Producto único:** "Suscripción Ecdótica Gramática"

| Campo | Valor |
|---|---|
| Tipo | Simple subscription (virtual) |
| Precio | **$7.99/mes** |
| Prueba gratuita | 7 días |
| Sign-up fee | $0 |
| Período | Mensual, indefinido hasta cancelación |
| Variante anual | **$71/año** (ahorra 25%) |

**Auto-enrollment vía Memberships:**

1. Membresía "Alumno Ecdótica Gramática"
2. Vinculada al producto de suscripción
3. En "Restrict Content" → Auto-enroll en los 4 cursos
4. Acceso expira al cancelar (no al instante, sino al fin del período pagado)

---

## 9. Content drip — la mecánica de retención

Configurar en `Tutor LMS Pro → Settings → Content Drip`:

**Tipo:** "Available after X days from enrollment"

| Nivel | Liberación |
|---|---|
| Nivel 1 | Disponible inmediatamente |
| Nivel 2 | Día 28 (preview a los 25 días vía email) |
| Nivel 3 | Día 56 |
| Nivel 4 | Día 98 (requiere solicitar plaza si el cap de 20 está lleno) |

Dentro de cada nivel, las lecciones se liberan **una por semana** o **secuencialmente al completar la anterior** (lo que mejor ajuste pedagógicamente).

**Por qué importa:** sin drip, el alumno consume todo en una semana y cancela. Con drip, hay ~5 meses garantizados de retención por alumno.

---

## 10. Flujo de compra del alumno

```
1. Visita ecdotica.com/gramatica
2. Ve landing con plan: $7.99/mes, 7 días gratis
3. Hace clic en "Empezar gratis"
4. WooCommerce checkout (ya conoce Stripe)
5. Crea cuenta + tarjeta
6. Stripe registra suscripción mensual (sin cobrar 7 días)
7. WooCommerce Memberships auto-enrolla en los 4 cursos
8. Tutor LMS muestra Nivel 1 disponible, niveles 2-4 bloqueados
9. Lecciones se liberan progresivamente
10. Al día 7: primer cobro automático $7.99
11. Si cancela: acceso hasta el fin del período pagado
```

---

## 11. Roadmap de implementación (6 semanas)

### Semana 1 — Infraestructura
- [ ] Backup completo de ecdotica.com
- [ ] Staging site (EasyWP "Create Staging")
- [ ] Instalar Tutor LMS + Tutor LMS Pro
- [ ] Instalar WooCommerce Subscriptions + Memberships
- [ ] Verificar Stripe Gateway con Subscriptions ("Accept recurring payments" ON)
- [ ] Crear cuenta en Bunny Stream → Video Library `ecdotica-gramatica`

### Semana 2 — Estructura
- [ ] Crear los 4 cursos vacíos en Tutor LMS
- [ ] Configurar Content Drip globalmente
- [ ] Crear producto de suscripción WooCommerce ($7.99/mes)
- [ ] Crear plan de membresía y vincularlo al producto
- [ ] Configurar auto-enroll en los 4 cursos
- [ ] Test: comprar suscripción con tarjeta de prueba Stripe `4242 4242 4242 4242`

### Semanas 3–4 — Contenido Nivel 1
- [ ] Guion + grabación de 4 lecciones (1 por semana del nivel)
- [ ] Crear quizzes (10 preguntas por lección)
- [ ] Subir vídeos a Bunny Stream con DRM básico
- [ ] Diseñar certificado del Nivel 1

### Semana 5 — Landing y diseño
- [ ] Página de ventas `/gramatica` con copy persuasivo
- [ ] Página de dashboard del alumno
- [ ] Emails transaccionales (bienvenida, recordatorio de prueba, lección desbloqueada, cobro exitoso, cobro fallido, cancelación, certificado)
- [ ] Plantillas de emails con branding Ecdótica Gramática
- [ ] Página `/mi-cuenta` con tabs: Mis cursos · Suscripción · Facturas · Certificados
- [ ] Política de cancelación visible y un solo clic
- [ ] FAQ con objeciones comunes

### Semana 6 — Pruebas, soft launch y métricas
- [ ] QA end-to-end (3 cuentas, 3 escenarios)
- [ ] Test de drip: forzar avance del reloj en staging
- [ ] Verificar revocación de acceso al fin del período al cancelar
- [ ] Verificar emisión automática del certificado al completar Nivel 1
- [ ] Conectar GA4 + eventos WooCommerce (`purchase`, `begin_checkout`, `add_to_cart`)
- [ ] Conectar Meta Pixel si habrá Ads
- [ ] Soft launch con 20–50 alumnos invitados
- [ ] Encuesta de 5 preguntas al terminar la primera lección
- [ ] Ajustar drip, copy o lecciones según feedback antes del lanzamiento público

---

## 12. KPIs y métricas a vigilar

| Métrica | Objetivo (primeros 6 meses) | Dónde se mide |
|---|---|---|
| CR landing → trial | 3–6% | GA4 (`begin_checkout` / sesiones a `/gramatica`) |
| CR trial → suscripción de pago | ≥ 50% | WooCommerce Subscriptions reports |
| Churn mensual | < 8% | WC Subscriptions → "Cancellations" |
| LTV (tiempo medio de vida × ARPU) | ≥ $32 (≥ 4 meses) | LTV = ARPU / churn |
| Tasa de finalización Nivel 1 | ≥ 60% | Tutor LMS → Reports → Course Completion |
| NPS al terminar Nivel 1 | ≥ 40 | Encuesta in-app post-certificado |
| **CAC** | **≤ $10 USD** | Gasto en ads / nuevos suscriptores pagos |

**Regla práctica:** mantener `LTV ≥ 3 × CAC` antes de escalar gasto en publicidad. Con LTV ~$32 y la regla 3×, el CAC máximo es $10–11.

---

## 13. Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Conflicto Tutor LMS ↔ Memberships ↔ Subscriptions | Media | Alto | Una sola capa de acceso (Memberships); no usar el "WC course product" de Tutor en paralelo |
| Carga del sitio se degrada con vídeos | Alta | Medio | Bunny Stream fuera de WP; CDN ya en Cloudflare |
| Stripe rechaza tarjetas LatAm | Media | Alto | Habilitar también PayPal Subscriptions como respaldo |
| Churn alto post Nivel 1 | Alta | Alto | Drip que abre Nivel 2 antes de cerrar Nivel 1 + email a los 25 días con preview |
| Pirateo de vídeos | Media | Bajo | DRM de Bunny Stream + watermark con email del alumno |
| Cuello de botella en tutoría Nivel 4 | Alta | Medio | Cap de 20 alumnos simultáneos; lista de espera; plantillas de feedback |
| Margen estrecho a $7.99 con CAC > $10 | Media | Alto | No escalar ads hasta que LTV ≥ 3×CAC esté comprobado en cohortes reales |
| Quiebre legal por facturación cross-border | Baja | Alto | T&C y política de privacidad revisados por abogado boliviano antes del lanzamiento |

---

## 14. Roadmap post-lanzamiento (mes 2 en adelante)

**Mes 2 — Optimización**
- Análisis de embudo (¿dónde se cae el alumno?)
- A/B test de copy en landing
- Test de precio anual ($71 vs $89)

**Mes 3 — Producir Nivel 2 y Nivel 3**
- Replicar pipeline de producción de Nivel 1
- Invitados especiales (profesores de la RAE Bolivia, autores del catálogo Nuevo Milenio)

**Mes 4 — Activar Nivel 4 con tutoría**
- Sistema de envío de textos del alumno (CPT `tutor_assignments`)
- Asignar Marcelo como instructor
- SLA público: feedback en ≤ 10 días

**Mes 5–6 — Expansión**
- Cursos satélite cortos ("Ortotipografía exprés", "Subjuntivo en 7 días")
- Plan anual con descuento permanente
- Programa de afiliados (10–20% comisión vía AffiliateWP)
- Integración con `ecdoticon` para que el chatbot recomiende cursos según la pregunta

**Mes 6+ — Bilingüe + Marketplace**
- Instalar WPML, traducir landing + Nivel 1 al inglés
- URLs `/en/grammar`
- Activar módulo marketplace de Tutor LMS
- Invitar 3–5 instructores con cursos complementarios (literatura, edición, narrativa)
- Reparto 70/30 (instructor/plataforma)

---

## 15. Inversión y proyección financiera

**Inversión año 1 (sin WPML):**

| Concepto | Costo |
|---|---|
| Licencias plugins | $637 |
| Producción audiovisual Nivel 1 (4 lecciones) | $400–$800 |
| Diseño landing + emails | $300 |
| Reserva para ads de soft launch | $500 |
| Bunny Stream primer año (estimado) | ~$120 |
| **Total año 1** | **$1.957–$2.357 USD** |

**Proyección conservadora ($7.99/mes):**

| Mes | Suscriptores activos | MRR | Acumulado |
|---|---|---|---|
| 1 | 30 | $240 | –$1.700 |
| 3 | 90 | $720 | –$700 |
| 6 | 200 | $1.600 | +$800 |
| 12 | 400 | $3.200 | +$15.000 |

**Punto de equilibrio estimado:** mes 6–7.

---

## 16. Lo que sí toca este repo (Ecdotica/)

Cuando todo esté funcionando en producción:

1. `wordpress-plugin/tutor-lms-customizations/` — versionar snippets PHP que se añadan al `functions.php` del tema (ajustes a certificado, emails, hooks de Tutor LMS).
2. `docs/programa-gramatica-setup.md` — IDs de cursos, producto y membresía. Son frágiles; si EasyWP migra el sitio pueden romperse.
3. Si más adelante se construye una integración entre `ecdoticon` y el LMS (que recomiende lecciones según la pregunta del usuario), ese código vive en `worker/ecdoticon.js`.
