# Sesión 03 — Discovery de Requerimientos y Refactoring Guiado por Tests
## Civic Tech Moncton 506 — Notas de Estudio

**Fecha:** 2026-07-02  
**Proyecto:** civictech-506  
**Objetivo:** Completar la spec del Application Lifecycle con reglas de negocio reales, alinear el módulo de validación con el Registration Form real de la organización, y ejecutar un refactor completo guiado por tests.

---

## PARTE 1 — Discovery de Requerimientos (la habilidad FDE en acción)

Esta sesión fue principalmente de **discovery**: extraer reglas de negocio reales que no eran visibles en los diagramas originales. Esta es la habilidad consultiva central de un Forward Deployed Engineer.

### Reglas descubiertas en esta sesión

**1. La revisión del admin es un checklist de verificación, no un simple botón.**
El admin verifica físicamente tres items contra los datos que el member ingresó:
- `volunteer_id` → verifica nombre y apellido
- `photograph` → verifica identidad
- `home_address` → verifica el campo address

Los documentos NO se suben al sistema — el member los presenta en persona; el sistema solo registra los hechos de verificación (quién verificó, qué, cuándo).

**2. El checklist BLOQUEA la aprobación.**
El sistema debe rechazar un intento de aprobación si algún item del checklist no está verificado. El rechazo, en cambio, NO requiere checklist completo — un admin puede rechazar en cualquier momento (asimetría deliberada).

**3. El motivo de rechazo se auto-genera.**
Si hay items sin verificar al momento del rechazo, el sistema genera el motivo automáticamente (ej. "unverified: photograph, home_address"). El admin puede agregar notas opcionales.

**4. Las solicitudes duplicadas fueron un problema operativo real.**
Los members creaban múltiples solicitudes de enrollment cuando se equivocaban al escribir su nombre. Mitigación: prevención de duplicados **por email** — pero consciente del estado:
- Existe solicitud activa (`SUBMITTED`/`VALIDATION_FAILED`/`STORED`) → bloquear
- Existe `APPROVED` → bloquear con mensaje "ya eres miembro"
- Solo existen `REJECTED` → permitir (consistente con la regla de re-aplicación)

**Limitación conocida documentada:** si el member escribe mal el EMAIL mismo, este chequeo no puede detectar el duplicado. Riesgo aceptado para v1. *Lección: declarar lo que el sistema NO cubre es marca de una spec profesional.*

**5. El Registration Form real es más simple que el propuesto.**
Campos reales (todos OBLIGATORIOS): `first_name`, `last_name`, `email`, `phone`, `address`.
Los campos `skills`, `availability_hours_per_week`, `experience_level`, `motivation`, `linkedin_or_github` pertenecen al proceso de **Onboarding**, no a Enrollment.

**6. La aprobación dispara una cadena de efectos (handoff hacia Onboarding).**
Al pasar a `APPROVED`: enviar email de aprobación → crear cuenta de usuario → habilitar acceso básico → enviar email de bienvenida invitando al portal de onboarding.
Decisión de diseño: **las decisiones de negocio no se revierten por fallas técnicas** — si la creación de cuenta falla, la solicitud permanece `APPROVED` y la falla se registra para resolución manual.

### Insight arquitectónico clave

Validación stateless vs stateful:

| | Stateless (validation.py) | Stateful (capa de servicio) |
|---|---|---|
| Mira | Solo el payload del formulario | Datos existentes (BD) |
| Ejemplo | "¿el email está bien formado?" | "¿este email ya tiene una solicitud?" |
| Vive en | Spec 01 / validation.py | Spec 02 / service.py (futuro) |

La prevención de duplicados es stateful → pertenece a la capa de servicio, NO al módulo de validación pura. Esto preserva el contrato "No DB. No side effects." de validation.py.

---

## PARTE 2 — Versionado de specs con changelog

Cuando los requerimientos cambian, la spec recibe una **nueva versión con changelog** — la historia de la decisión queda visible:

```markdown
## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-06-30 | Initial draft with proposed fields |
| 2.0 | 2026-07-02 | Aligned with the real organizational Registration Form: ... |
```

El changelog responde la pregunta futura "¿por qué cambió esto?" sin arqueología en el historial de Git.

---

## PARTE 3 — Refactoring Guiado por Tests (la técnica principal de esta sesión)

### El orden contraintuitivo

Cuando la spec cambia, el refactor sigue este orden:

```
1. Actualizar la SPEC       (el contrato cambia primero)
2. Actualizar los TESTS     (los tests codifican el nuevo contrato)
3. Correr pytest            (ROJO — fallas masivas, y eso es CORRECTO)
4. Refactorizar el CÓDIGO   (guiado por los tests en rojo)
5. Correr pytest            (VERDE — refactor completo y verificado)
```

**Por qué tests antes que código:** los tests en rojo se convierten en el mapa exacto del trabajo. Cada FAILED te dice con precisión qué es lo que el código todavía no hace. Cuando todo está en verde, tenés PRUEBA de que el refactor está completo — no una sensación, una verificación.

### Nuestros números en esta sesión

```
Después de actualizar tests:  22 failed, 5 passed   ← el mapa
Después de refactorizar:      27 passed              ← la prueba
```

**Detalle revelador:** los 5 tests que sobrevivieron la fase roja fueron los de `email` (sin cambios entre v1/v2) y `phone_invalid_format` (mismo mensaje de error en ambas versiones). Los tests te dicen qué sobrevive un cambio de spec con precisión quirúrgica.

### El mapa del refactor (qué cambió en validation.py)

```
ELIMINADO:   validate_full_name, validate_skills, validate_availability,
             validate_experience_level, validate_motivation,
             validate_linkedin_or_github
             + constantes VALID_SKILLS, VALID_EXPERIENCE_LEVELS (código muerto)

CREADO:      validate_first_name, validate_last_name, validate_address

MODIFICADO:  validate_phone (opcional → requerido)

SIN TOCAR:   validate_email, ValidationResult, imports

ACTUALIZADO: validate_registration_form (orquestador con los 5 campos reales)
```

### El cambio de patrón: opcional → requerido

Este fue el cambio conceptual en `validate_phone`:

```python
# v1 — campo OPCIONAL: la ausencia está bien, salir en silencio
def validate_phone(phone, errors):
    if not phone or not phone.strip():
        return                    # ← sin error, solo salir

# v2 — campo REQUERIDO: la ausencia ES un error
def validate_phone(phone, errors):
    if not phone or not phone.strip():
        errors.append("phone is required")   # ← la diferencia de una línea
        return
```

### El código muerto debe morir

Después de eliminar las funciones que usaban `VALID_SKILLS` y `VALID_EXPERIENCE_LEVELS`, las constantes quedaron como código muerto. El código muerto es deuda: el próximo lector va a buscar dónde se usa y no va a encontrar nada. Eliminarlo es parte del refactor, no una limpieza opcional.

---

## PARTE 4 — Decisiones de diseño para recordar

**1. Mínimo 2 caracteres para nombres (no 3).**
Apellidos reales como "Li", "Ng", "Wu" existen. Las reglas de validación deben acomodar datos del mundo real, no datos idealizados.

**2. La misma entidad Application a través del correction loop.**
El correction loop reutiliza la misma Application transicionando de vuelta a `SUBMITTED` — no una Application nueva por intento. La trazabilidad viene de una **tabla de historial de transiciones**, no de duplicación de entidades:

```
ApplicationStatusTransition
├── application_id
├── from_status / to_status
├── timestamp
├── triggered_by  (member | system | admin)
└── notes
```

**3. Congelar datos durante la revisión.**
Un member no puede modificar una solicitud en `STORED` — el admin no debe evaluar un blanco móvil.

**4. Los estados terminales son inmutables.**
`APPROVED` y `REJECTED` rechazan toda transición. Re-aplicar después del rechazo = solicitud NUEVA; la rechazada queda cerrada para auditoría.

---

## PARTE 5 — Nota sobre el entorno Zsh

Después de cambiar de bash a Zsh, `uv` desapareció (`command not found`). Causa: el instalador agregó `uv` al PATH de bash (`~/.bashrc`), pero Zsh lee `~/.zshrc`.

Solución (permanente):
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

*Lección: al cambiar de shell, las personalizaciones del PATH deben migrarse. Cada shell tiene su propio archivo de configuración.*

---

## PARTE 6 — Estado actual del proyecto

```
Spec 01 v2.0 ✅ → validation.py v2 ✅ → 27 tests ✅  (mergeado vía PR)
Spec 02 v1.0 ✅ → enums.py + models.py ⬜  ← PRÓXIMA SESIÓN
```

**Verificación pendiente:** confirmar en GitHub que el PR de la spec 02 realmente se mergeó a dev (puede haber un PR viejo abierto — la pestaña Pull Requests mostraba 1 abierto).

### Adelanto de la próxima sesión
- `enums.py` — `ApplicationStatus` usando `Enum`/`StrEnum` de Python (concepto nuevo, mapea al `enum` de C# con extras)
- `models.py` — la máquina de estados `Application` implementando la matriz de transiciones de la spec 02 sección 5
- `tests/enrollment/test_application_lifecycle.py`

---

*Documento generado: 2026-07-02 | civictech-506 | Sesión 03*
