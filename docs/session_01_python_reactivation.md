# Sesión 01 — Python Reactivation
## Civic Tech Moncton 506 — Documento de Estudio

**Fecha:** 2026-06-30  
**Proyecto:** civictech-506  
**Objetivo:** Reactivación de Python + Setup del entorno + Primer módulo real

---

## PARTE 1 — Entorno de Desarrollo

### Stack instalado y verificado

| Herramienta | Versión | Para qué sirve |
|---|---|---|
| Ubuntu | 26.04 LTS "Resolute" | Sistema operativo base |
| Git | 2.53.0 | Control de versiones |
| Python | 3.13.14 y 3.14.6 | Lenguaje principal |
| uv | 0.11.26 | Manejador de paquetes y entornos virtuales |
| Docker | 29.6.1 | Contenedores (Fase 2) |
| Docker Compose | v5.2.0 | Orquestar múltiples contenedores |
| Claude Code | v2.1.197 + Sonnet 4.6 | Agente de codificación con IA |
| VS Code | — | IDE principal |

---

### `uv` — el manejador moderno de Python

`uv` reemplaza a `pip`, `venv`, `pyenv` y `poetry` en un solo comando. Es 10-100x más rápido.

```bash
# Crear un nuevo proyecto
uv init nombre-proyecto --python 3.13
cd nombre-proyecto

# Agregar dependencias
uv add fastapi pandas requests

# Correr un script
uv run main.py

# Correr Python interactivo
uv run python
```

**Por qué no usar el Python del sistema en Ubuntu:**
Ubuntu usa Python internamente para el sistema operativo. Si lo modificás, podés romper el sistema. `uv` crea entornos aislados por proyecto — el Python del sistema no se toca nunca.

---

### Estructura de carpetas del proyecto

```
civictech-506/
├── shared/
│   └── domain/
│       └── person.py              # Shared Kernel mínimo (PersonId, email, nombre)
├── modules/
│   └── community_lifecycle/        # Bounded Context 1
│       ├── domain/
│       │   ├── member.py
│       │   └── value_objects.py
│       └── enrollment/             # Proceso actual
│           ├── models.py
│           ├── enums.py
│           ├── validation.py       ← lo que construimos hoy
│           ├── repository.py
│           ├── service.py
│           └── routes.py
├── specs/
│   └── enrollment/
│       └── 01_validation_rules.md  ← primer documento SDD
├── api/
│   └── main.py
└── tests/
```

---

### Git — estructura de branches profesional

```
main      ← producción, siempre estable
staging   ← pre-producción, integración y pruebas
dev       ← desarrollo activo, base de trabajo diario
feature/* ← una rama por feature, merge a dev
```

**Flujo de trabajo:**
```
feature/mi-feature → dev → staging → main
```

**Comandos esenciales:**
```bash
# Crear y cambiar a una rama nueva
git checkout -b feature/nombre-feature

# Ver todas las ramas
git branch -a

# Subir rama al remote
git push -u origin feature/nombre-feature

# Traer cambios del remote
git pull origin dev

# Configuración global de pull (una sola vez)
git config --global pull.rebase false
git config --global user.email "tu@email.com"
git config --global user.name "Tu Nombre"
```

**SSH a GitHub:**
```bash
# Generar llave SSH
ssh-keygen -t ed25519 -C "tu@email.com"

# Ver la llave pública para copiar a GitHub
cat ~/.ssh/id_ed25519.pub

# Verificar conexión
ssh -T git@github.com
```

---

## PARTE 2 — Arquitectura y Diseño

### Por qué Monolito Modular (no Microservicios)

Microservicios resuelven problemas de **escala organizacional** (múltiples equipos deployando independientemente) y **escala de tráfico diferenciada**. Para un solo desarrollador con un dominio acotado, el costo supera el beneficio:

- Comunicación entre servicios (HTTP, message queues) — complejidad innecesaria
- Transacciones distribuidas — problemas de consistencia
- Debugging más difícil — el bug puede estar en la red
- Multiplicás el trabajo de DevOps por N servicios

**La decisión correcta:** Monolito Modular con bounded contexts bien definidos. Si el proyecto crece y hay necesidad real de escala, los módulos ya están listos para extraerse como servicios — sin refactorizar el dominio.

---

### Domain-Driven Design (DDD) — Bounded Contexts

Un **bounded context** es una frontera donde un lenguaje ubicuo (términos del negocio) tiene un significado específico y consistente.

**Los 4 bounded contexts de civictech-506:**

| Contexto | Procesos | Entidad central |
|---|---|---|
| Community & Volunteer Lifecycle | Enrollment, Onboarding, Engagement, Recognition | `Member` |
| Challenge Intake & Project Delivery | Challenge Intake, Project Scoping, Solution Dev, Delivery | `Project` |
| Community Partnerships & Outreach | Institutional Partnerships, Events, Advocacy, PR | `Partnership` / `Event` |
| Governance & Operations | Strategic Planning, Resources, Compliance, Performance | `Resource` / `Metric` |

**Shared Kernel** — lo mínimo verdaderamente universal:
```python
# shared/domain/person.py
# SOLO identidad: PersonId, email, full_name. Nada más.
```

Cada contexto tiene su propia "vista" de la persona con los datos que le importan, relacionados por `PersonId`. Evita el "God Object".

**Enrollment NO es un bounded context** — es un proceso dentro de `Community & Volunteer Lifecycle`.

---

### Spec-Driven Development (SDD) Ligero

SDD es una metodología donde la especificación — no el código — es la fuente de verdad.

**El flujo que usamos:**
```
Specify → Plan → Implement
```

**Notación EARS** (Easy Approach to Requirements Syntax):
```
WHEN [condición], IF [situación], THEN [el sistema SHALL hacer X]
```

Ejemplo real:
```
WHEN el sistema recibe un Registration Form,
IF full_name contiene menos de 3 caracteres,
THEN el sistema SHALL agregar el error "full_name must be at least 3 characters"
```

**Estructura en el repo:**
```
specs/
└── enrollment/
    ├── 01_validation_rules.md    ← spec actual
    ├── 02_application_lifecycle.md
    └── 03_api_contracts.md
```

**Regla de uso con Cursor/Claude Code en Fase 1:**
- ✅ Usá el chat como **tutor** ("¿por qué funciona así?", "¿cómo se compara con C#?")
- ❌ No dejes que el agente escriba la lógica core por vos — perdés el aprendizaje

---

## PARTE 3 — Conceptos de Python Aprendidos

### 1. `set` vs `list` — O(1) vs O(n)

```python
# list — busca elemento por elemento (O(n))
"Python" in ["Python", "JavaScript", "Frontend"]  # revisa uno por uno

# set — tabla hash, búsqueda instantánea (O(1))
"Python" in {"Python", "JavaScript", "Frontend"}  # va directo al valor
```

**Equivalente en C#:**
```csharp
var list = new List<string> { "Python" };
list.Contains("Python");  // O(n)

var set = new HashSet<string> { "Python" };
set.Contains("Python");  // O(1)
```

**Regla práctica:** Si solo vas a preguntar "¿está este elemento?" y el orden no importa → usá `set`.

---

### 2. `@dataclass` y `field(default_factory=list)`

```python
from dataclasses import dataclass, field

@dataclass
class ValidationResult:
    validation_passed: bool = False
    errors: list[str] = field(default_factory=list)  # ← correcto
    # errors: list[str] = []  ← PELIGROSO, no hagas esto
```

**Por qué `= []` es peligroso — el Mutable Default Argument Trap:**

```python
# Con = [] (MAL)
r1 = ValidationResult()
r2 = ValidationResult()
r1.errors.append("email is required")
print(r2.errors)  # ["email is required"] ← MISMO objeto compartido

# Con field(default_factory=list) (BIEN)
r1 = ValidationResult()
r2 = ValidationResult()
r1.errors.append("email is required")
print(r2.errors)  # [] ← lista propia, correcta
```

**La trampa:** en Python, `= []` en una clase crea UNA sola lista en tiempo de definición, compartida por TODAS las instancias. `default_factory=list` crea una lista nueva por cada instancia.

**Aplica a todo objeto mutable como default:** `list`, `dict`, `set`.

**Equivalente en C#:**
```csharp
// C# crea una lista nueva por instancia automáticamente
public List<string> Errors { get; set; } = new List<string>();
// Python necesita indicarlo explícitamente con default_factory
```

---

### 3. Type hints — `str | None`

```python
# Python 3.10+ — el operador | significa "puede ser este tipo O este otro"
def validate_full_name(name: str | None, errors: list[str]) -> None:
    ...
```

**Equivalente en C#:**
```csharp
void ValidateFullName(string? name, List<string> errors) { }
```

`-> None` = `void` en C#.

Los tipos son opcionales en runtime en Python, pero los declaramos para:
- Que Pylance/Ruff detecten errores mientras escribís
- Documentar la intención
- Herramientas de testing los usan para generar casos automáticamente

---

### 4. `re.match()` — Expresiones regulares

```python
import re

# Validar nombre — solo letras (incluyendo acentos franceses) y espacios
re.match(r"^[a-zA-ZÀ-ÿ\s]+$", name)

# Validar email
pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
re.match(pattern, email)

# Validar teléfono canadiense
re.match(r"^(\+1)?\d{10}$", phone)
```

**Desglose del patrón de nombre:**
| Parte | Significado |
|---|---|
| `^` | Desde el primer carácter |
| `[a-zA-Z]` | Letras minúsculas y mayúsculas |
| `À-ÿ` | Caracteres latinos extendidos (tildes, diéresis, ç) |
| `\s` | Espacios |
| `+` | Uno o más caracteres |
| `$` | Hasta el último carácter |

**Por qué regex y no `"@" in email`:**
`"@" in email` aprueba `"@gmail.com"`, `"ronald@"`, `"ronald@@gmail"` — todos inválidos. La regex exige estructura completa: parte local + @ + dominio + extensión.

---

### 5. `.strip()` — equivalente a `.Trim()` de C#

```python
"  ronald@gmail.com  ".strip()   # → "ronald@gmail.com"
"  hola  ".lstrip()              # → "hola  " (solo inicio)
"  hola  ".rstrip()              # → "  hola" (solo final)
```

| C# | Python |
|---|---|
| `.Trim()` | `.strip()` |
| `.TrimStart()` | `.lstrip()` |
| `.TrimEnd()` | `.rstrip()` |

**Por qué usarlo en validación:** los usuarios suelen agregar espacios accidentales al escribir o copiar/pegar. Sin `.strip()`, `"ronald@gmail.com "` (con espacio al final) fallaría la validación aunque el email esté bien escrito.

---

### 6. Set Comprehension

```python
# Set comprehension — produce un set
invalid = {s for s in skills if s not in VALID_SKILLS}

# Equivalente en C# (LINQ)
var invalid = skills.Where(s => !validSkills.Contains(s)).ToHashSet();

# Equivalente en Python sin comprehension (loop explícito)
invalid = set()
for s in skills:
    if s not in VALID_SKILLS:
        invalid.add(s)
```

**Estructura de cualquier comprehension:**
```python
{expresión for variable in iterable if condición}
#  ↑ qué     ↑ de dónde viene    ↑ filtro opcional
```

**Los tres sabores:**
```python
[s for s in skills if ...]    # list comprehension → produce list
{s for s in skills if ...}    # set comprehension  → produce set
{k: v for k, v in d.items()}  # dict comprehension → produce dict
```

---

### 7. `.get()` vs `[]` en diccionarios

```python
form = {"email": "ronald@gmail.com"}

form["full_name"]        # → KeyError si la clave no existe ← crash
form.get("full_name")    # → None si la clave no existe ← seguro
```

**Equivalente en C#:**
```csharp
dict.TryGetValue("full_name", out var value) ? value : null;
```

**Regla práctica:** cuando el dict viene de input externo (formulario, API, JSON), siempre usá `.get()` — no podés garantizar que el usuario envió todos los campos.

---

### 8. `isinstance` + el bug de `bool` subclasificando `int`

```python
# En Python, bool es subclase de int — sorpresa para devs de C#
isinstance(True, int)   # → True
isinstance(False, int)  # → True
True == 1               # → True
False == 0              # → True
True + True             # → 2

# El bug silencioso
hours = True
isinstance(hours, int)           # → True ← pasa el chequeo de tipo
hours < 1 or hours > 40         # → False (True == 1, entre 1 y 40)
# resultado: True pasa como "1 hora" ← incorrecto
```

**La solución — excluir bool explícitamente:**
```python
if not isinstance(hours, int) or isinstance(hours, bool):
    errors.append("availability_hours_per_week must be a number")
```

**En C# este problema no existe** — `bool` y `int` son tipos completamente separados, el compilador no lo permite.

---

### 9. `__init__.py` — por qué existe

Para que Python reconozca una carpeta como **paquete importable**, necesita un archivo `__init__.py` (puede estar vacío).

```bash
# Sin __init__.py
from modules.community_lifecycle.enrollment.validation import ...
# → ModuleNotFoundError

# Con __init__.py en cada carpeta del path
touch modules/__init__.py
touch modules/community_lifecycle/__init__.py
touch modules/community_lifecycle/enrollment/__init__.py
# → funciona
```

**La traducción de import a ruta de archivo:**
```python
from modules.community_lifecycle.enrollment.validation import validate_registration_form
#    ↓
#    modules/community_lifecycle/enrollment/validation.py
```

Cada punto es un separador de carpeta. El último nombre es el archivo `.py`.

---

### 10. Patrón acumulador de errores

En vez de retornar una lista de errores por función y concatenar al final, pasamos la misma lista a todas las funciones:

```python
# Todas las funciones reciben y modifican la MISMA lista
def validate_full_name(name: str | None, errors: list[str]) -> None:
    errors.append("error aquí si falla")

def validate_registration_form(form: dict) -> ValidationResult:
    result = ValidationResult()
    validate_full_name(form.get("full_name"), result.errors)
    validate_email(form.get("email"), result.errors)
    # ... más validaciones ...
    result.validation_passed = len(result.errors) == 0
    return result
```

**Por qué:** la spec dice "correr TODAS las reglas antes de retornar". Con el acumulador, al terminar la última función ya tenés todos los errores sin concatenación extra.

---

### 11. Fail-fast local vs global

```python
# Fail-fast GLOBAL — prohibido por la spec
# (no pares entre campos distintos)

# Fail-fast LOCAL — correcto dentro de un mismo campo
def validate_full_name(name: str | None, errors: list[str]) -> None:
    if not name or not name.strip():
        errors.append("full_name is required")
        return  # ← sale de la función, NO de toda la validación
    # Si llegamos acá, name existe — tiene sentido chequear longitud y formato
    if len(name) < 3:
        errors.append("full_name must be at least 3 characters")
```

**La regla:** entre campos → no fail-fast. Dentro de un campo → fail-fast después del error fundamental (no tiene sentido chequear longitud si el campo está vacío).

---

### 12. Campo requerido vs campo opcional — patrones

```python
# Campo REQUERIDO — ausencia = error
def validate_full_name(name: str | None, errors: list[str]) -> None:
    if not name or not name.strip():
        errors.append("full_name is required")
        return  # sale con error agregado

# Campo OPCIONAL — ausencia = ok
def validate_phone(phone: str | None, errors: list[str]) -> None:
    if not phone or not phone.strip():
        return  # sale sin error — es válido no tener teléfono
    # Si llegamos acá, el campo vino — validamos formato
    if not re.match(pattern, phone.strip()):
        errors.append("phone format is invalid")
```

---

## PARTE 4 — El archivo `validation.py` completo

```python
"""
Enrollment Validation Rules
Spec: specs/enrollment/01_validation_rules.md

Pure, stateless validation. No DB. No side effects.
Given a form payload → returns validation result + all errors found.
"""

import re
from dataclasses import dataclass, field

# Predefined valid skills (spec section 2.4)
VALID_SKILLS = {
    "Python", "JavaScript", "Frontend", "Backend", "DevOps",
    "Data", "Project Management", "Design", "Communications",
    "Legal", "Finance"
}

# Valid experience levels (spec section 2.6)
VALID_EXPERIENCE_LEVELS = {"Beginner", "Intermediate", "Advanced"}


@dataclass
class ValidationResult:
    validation_passed: bool = False
    errors: list[str] = field(default_factory=list)


def validate_full_name(name: str | None, errors: list[str]) -> None:
    if not name or not name.strip():
        errors.append("full_name is required")
        return
    name = name.strip()
    if len(name) < 3:
        errors.append("full_name must be at least 3 characters")
    if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", name):
        errors.append("full_name must contain only letters and spaces")


def validate_email(email: str | None, errors: list[str]) -> None:
    if not email or not email.strip():
        errors.append("email is required")
        return
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email.strip()):
        errors.append("email format is invalid")


def validate_phone(phone: str | None, errors: list[str]) -> None:
    if not phone or not phone.strip():
        return
    pattern = r"^(\+1)?\d{10}$"
    if not re.match(pattern, phone.strip().replace(" ", "").replace("-", "")):
        errors.append("phone format is invalid")


def validate_skills(skills: list[str] | None, errors: list[str]) -> None:
    if not skills:
        errors.append("at least one skill is required")
        return
    invalid = {s for s in skills if s not in VALID_SKILLS}
    if invalid:
        errors.append(f"skills contains invalid values: {', '.join(sorted(invalid))}")


def validate_availability(hours: int | None, errors: list[str]) -> None:
    if hours is None:
        errors.append("availability_hours_per_week is required")
        return
    if not isinstance(hours, int) or isinstance(hours, bool):
        errors.append("availability_hours_per_week must be a number")
        return
    if hours < 1 or hours > 40:
        errors.append("availability_hours_per_week must be between 1 and 40")


def validate_experience_level(level: str | None, errors: list[str]) -> None:
    if not level or not level.strip():
        errors.append("experience_level is required")
        return
    if level.strip() not in VALID_EXPERIENCE_LEVELS:
        errors.append("experience_level must be Beginner, Intermediate or Advanced")


def validate_motivation(motivation: str | None, errors: list[str]) -> None:
    if not motivation or not motivation.strip():
        errors.append("motivation is required")
        return
    if len(motivation.strip()) < 20:
        errors.append("motivation must be at least 20 characters")


def validate_linkedin_or_github(url: str | None, errors: list[str]) -> None:
    if not url or not url.strip():
        return
    if not url.strip().startswith("https://"):
        errors.append("linkedin_or_github must be a valid URL (https://)")


def validate_registration_form(form: dict) -> ValidationResult:
    result = ValidationResult()

    validate_full_name(form.get("full_name"), result.errors)
    validate_email(form.get("email"), result.errors)
    validate_phone(form.get("phone"), result.errors)
    validate_skills(form.get("skills"), result.errors)
    validate_availability(form.get("availability_hours_per_week"), result.errors)
    validate_experience_level(form.get("experience_level"), result.errors)
    validate_motivation(form.get("motivation"), result.errors)
    validate_linkedin_or_github(form.get("linkedin_or_github"), result.errors)

    result.validation_passed = len(result.errors) == 0
    return result
```

---

## PARTE 5 — Próximos pasos

### Próxima sesión
- **Tests formales con `pytest`** — verificar que `validation.py` cumple la spec punto por punto
- Esto cierra el ciclo SDD: spec → código → tests

### Plan general (recordatorio)
| Semanas | Foco | Entregable |
|---|---|---|
| 1-4 | Python + dominio | validation.py ✅, models.py, enums.py, FastAPI |
| 5-9 | Docker + AWS | App contenedorizada en cloud |
| 10-13 | LLMs / RAG / Agentes | Integración con IA |
| 14-16 | Portfolio + narrativa | Proyecto completo + pitch del gap |

### Recursos de referencia
- **Fred Baptiste Python Deep Dive Part 1** (Udemy) — buscar: "mutable default", "dataclass", "closures"
- **Real Python** (realpython.com) — tutoriales puntuales por concepto
- **FastAPI tutorial oficial** (fastapi.tiangolo.com) — semana 3
- **Kaggle Pandas micro-course** — semana 3

---

*Documento generado: 2026-06-30 | civictech-506 | feature/enrollment-validation*
