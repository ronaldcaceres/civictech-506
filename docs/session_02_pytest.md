# Sesión 02 — Testing con pytest
## Civic Tech Moncton 506 — Notas de Estudio

**Fecha:** 2026-07-01  
**Proyecto:** civictech-506  
**Objetivo:** Escribir un suite de tests formal para `validation.py`, cerrando el ciclo SDD

---

## PARTE 1 — Qué es pytest y por qué lo usamos

`pytest` es el framework de testing más usado en el ecosistema de Python. Verifica que nuestro código se comporte como la especificación lo exige.

**Instalarlo como dependencia de desarrollo:**
```bash
uv add pytest --dev
```

`--dev` significa que pytest solo se necesita durante el desarrollo, no en producción. Es el equivalente a `devDependencies` en npm.

**Verificar la instalación:**
```bash
uv run pytest --version
```

**Correr el suite de tests:**
```bash
# Correr un archivo específico
uv run pytest tests/enrollment/test_validation.py -v

# Correr todos los tests de la carpeta tests/
uv run pytest tests/ -v
```

La bandera `-v` significa "verbose" — muestra el nombre de cada test y su resultado, en vez de solo un punto por test.

---

## PARTE 2 — Cómo pytest encuentra y ejecuta los tests

pytest sigue tres reglas automáticas — sin configuración necesaria:

1. Busca **archivos** que empiezan con `test_`
2. Dentro de esos archivos, busca **funciones** que empiezan con `test_`
3. Ejecuta esas funciones y reporta pass/fail

**Por eso el nombre importa:**
```python
def valid_form():          # ← NO empieza con test_ → pytest lo IGNORA
def test_valid_form_passes():  # ← empieza con test_ → pytest lo EJECUTA
```

**Comparación con C#:**
```csharp
// C# — requiere una clase, atributos, y un test runner
[TestClass]
public class ValidationTests
{
    [TestMethod]
    public void TestFullName() { ... }
}
```
```python
# Python/pytest — solo una función con el nombre correcto. Sin clase, sin atributos.
def test_full_name():
    ...
```

pytest es notablemente más simple que NUnit o xUnit — sin código repetitivo (boilerplate).

---

## PARTE 3 — La sentencia `assert`

pytest usa la palabra clave nativa `assert` de Python. Si la condición es `True`, el test pasa silenciosamente. Si es `False`, el test falla y pytest muestra un mensaje detallado.

```python
def test_valid_form_passes():
    result = validate_registration_form(valid_form())
    assert result.validation_passed is True
    assert result.errors == []
```

**Comparación con C#:**
```csharp
// C# — métodos de aserción explícitos
Assert.IsTrue(result.ValidationPassed);
Assert.AreEqual(0, result.Errors.Count);
```
```python
# Python — assert simple con cualquier expresión booleana
assert result.validation_passed is True
assert result.errors == []
```

**Patrones de aserción usados en esta sesión:**
```python
assert result.validation_passed is True      # chequeo booleano
assert result.errors == []                     # chequeo de igualdad
assert "error message" in result.errors        # chequeo de pertenencia (¿está X en la lista?)
assert len(result.errors) >= 6                 # chequeo de comparación
```

**Por qué `is True` y no `== True`:**
`is` chequea identidad (mismo objeto en memoria), `==` chequea igualdad (mismo valor). Para booleanos y `None`, siempre usá `is` — es la convención pythonica y ligeramente más estricta.

---

## PARTE 4 — El patrón de función helper

En vez de reconstruir el formulario completo en cada test, creamos un helper que retorna un formulario válido conocido. Cada test parte de esa base y sobrescribe solo el campo que quiere probar.

```python
def valid_form() -> dict:
    """Retorna un formulario de registro completo y válido.
    Usalo como base y sobrescribí campos específicos en cada test."""
    return {
        "full_name": "Ronald Caceres",
        "email": "ronald.caceres@gmail.com",
        "phone": "5065551234",
        "skills": ["Python", "Backend"],
        "availability_hours_per_week": 10,
        "experience_level": "Intermediate",
        "motivation": "I want to contribute to my community through technology.",
        "linkedin_or_github": "https://github.com/ronaldcaceres",
    }
```

**Cómo cada test lo usa:**
```python
def test_full_name_too_short():
    form = valid_form()           # parte de un formulario válido
    form["full_name"] = "RR"     # sobrescribe SOLO el campo bajo prueba
    result = validate_registration_form(form)
    assert result.validation_passed is False
    assert "full_name must be at least 3 characters" in result.errors
```

**Por qué importa:**
- Cada test se enfoca en **una sola cosa** — un campo, una regla
- Si la lógica de validación cambia, actualizás el formulario base en un solo lugar
- Los tests quedan legibles y cortos

En C# esto se hace a menudo con un método `[TestInitialize]` o un patrón builder. En pytest, una simple función helper es suficiente.

---

## PARTE 5 — Tipos de tests que escribimos

Un suite de tests completo cubre más que solo el camino feliz (happy path). Escribimos 30 tests en estas categorías:

### 5.1 Happy path (camino feliz)
Confirma que un input válido pasa.
```python
def test_valid_form_passes():
    result = validate_registration_form(valid_form())
    assert result.validation_passed is True
```

### 5.2 Campos requeridos
Confirma que campos requeridos ausentes producen errores.
```python
def test_full_name_required():
    form = valid_form()
    form["full_name"] = ""
    result = validate_registration_form(form)
    assert "full_name is required" in result.errors
```

### 5.3 Campos opcionales
Confirma que los campos opcionales son válidos cuando están ausentes.
```python
def test_phone_optional_when_absent():
    form = valid_form()
    del form["phone"]            # elimina la clave por completo
    result = validate_registration_form(form)
    assert result.validation_passed is True
```

### 5.4 Valores límite (boundary values)
Prueba los bordes exactos de un rango numérico.
```python
def test_availability_below_minimum():   # 0 (justo por debajo de 1)
    form["availability_hours_per_week"] = 0
    # ... espera error

def test_availability_above_maximum():   # 41 (justo por encima de 40)
    form["availability_hours_per_week"] = 41
    # ... espera error
```
Los tests de límite atrapan bugs "off-by-one" — los errores numéricos más comunes.

### 5.5 Validación de formato
Prueba que los formatos inválidos sean rechazados.
```python
def test_email_missing_domain():
    form["email"] = "ronald@"     # falta el dominio
    # ... espera "email format is invalid"

def test_email_missing_local_part():
    form["email"] = "@gmail.com"  # falta la parte local
    # ... espera "email format is invalid"
```

### 5.6 Casos límite específicos de nuestro dominio
```python
def test_full_name_with_french_accents():  # René debe ser válido (ciudad bilingüe)
    form["full_name"] = "René Tremblay"
    assert result.validation_passed is True

def test_availability_bool_rejected():       # True NO debe contar como 1
    form["availability_hours_per_week"] = True
    assert "availability_hours_per_week must be a number" in result.errors
```

### 5.7 Iterar sobre múltiples valores válidos
```python
def test_experience_level_valid_values():
    for level in ["Beginner", "Intermediate", "Advanced"]:
        form = valid_form()
        form["experience_level"] = level
        result = validate_registration_form(form)
        assert result.validation_passed is True, f"Expected {level} to be valid"
```
Nota el mensaje después de la coma — solo se imprime si la aserción falla, diciéndote exactamente qué valor rompió el test.

### 5.8 Comportamiento agregado
Verifica la regla de "no fail-fast" de la spec.
```python
def test_all_rules_run_no_fail_fast():
    """Verifica que TODAS las reglas corran aunque múltiples campos fallen."""
    form = {
        "full_name": "", "email": "", "skills": [],
        "availability_hours_per_week": None,
        "experience_level": "", "motivation": "",
    }
    result = validate_registration_form(form)
    assert len(result.errors) >= 6   # los 6 campos requeridos reportan su error
```

---

## PARTE 6 — Leer el output de pytest cuando un test falla

Los mensajes de error de pytest son precisos. Este es el bug real que atrapamos en esta sesión:

```
AssertionError: assert 'full_name is required' in ['full name is required']
#                        ↑ guión bajo (esperado)   ↑ espacio (actual)
```

pytest te dice:
- Lo que esperabas: `'full_name is required'` (con guión bajo)
- Lo que el código retornó: `'full name is required'` (con espacio)
- Exactamente qué línea falló

**El bug:** `validation.py` tenía `"full name is required"` (espacio) en vez de `"full_name is required"` (guión bajo). El test manual no lo detectó porque leímos el output rápido; pytest lo atrapó al instante.

**Por qué este bug importaba:** un cliente de API que espera el nombre de campo `full_name` en la respuesta de error nunca haría match con `full name`. Este tipo de inconsistencia silenciosa rompe los contratos entre sistemas — exactamente el tipo de cosa que los tests existen para prevenir.

---

## PARTE 7 — El ciclo SDD, ahora completo

```
Spec (01_validation_rules.md)      ← define QUÉ debe hacer el sistema
  → Código (validation.py)          ← implementa las reglas
    → Tests (test_validation.py)    ← verifica que el código cumple la spec
      → Bug encontrado y corregido ✅
```

Cada test se puede rastrear a una regla en la spec. Esta trazabilidad es lo que hace que el código sea profesional y mantenible.

---

## PARTE 8 — Flujo de Git usado en esta sesión

```bash
# Crear feature branch
git checkout -b feature/enrollment-validation-test

# Preparar y commitear
git add tests/ modules/community_lifecycle/enrollment/validation.py
git commit -m "test: add enrollment validation test suite (30 tests, all passing)"

# Subir
git push origin feature/enrollment-validation-test

# En GitHub: crear PR → base branch dev → merge

# Sincronizar dev local
git checkout dev
git pull origin dev
```

**Comandos aprendidos sobre git fetch:**
```bash
git fetch                          # actualiza info de TODAS las ramas remotas
git fetch origin branch-name       # actualiza info de UNA rama específica
git fetch origin branch -- file    # extrae un archivo específico de una rama remota

# Inspeccionar antes de hacer pull
git log dev..origin/dev --oneline  # commits en el remoto que no tenés localmente
git diff dev origin/dev            # diferencias de archivos
```

**Distinción clave:**
- `git fetch` = mirar qué cambió en el remoto, sin tocar el código local
- `git pull` = fetch + merge en la rama actual

---

## PARTE 9 — Próximos pasos

### Próxima sesión
- **Modelado del dominio** — modelo `Application`, enum `ApplicationStatus`, la máquina de estados (`PENDING → STORED → APPROVED/REJECTED`)
- Esto corresponde a `specs/enrollment/02_application_lifecycle.md` (a crear)

### Plan general (recordatorio)
| Semanas | Foco | Entregable |
|---|---|---|
| 1-4 | Python + dominio | validation.py ✅, tests ✅, models.py, enums.py, FastAPI |
| 5-9 | Docker + AWS | App contenedorizada en cloud |
| 10-13 | LLMs / RAG / Agentes | Integración con IA |
| 14-16 | Portfolio + narrativa | Proyecto completo + pitch del gap |

### Recursos de referencia
- **pytest official docs** (docs.pytest.org) — la referencia definitiva
- **Real Python — "Getting Started With pytest"** — tutorial práctico
- **Fred Baptiste Python Deep Dive** — para conceptos de Python más profundos según se necesiten

---

*Documento generado: 2026-07-01 | civictech-506 | Sesión 02*
