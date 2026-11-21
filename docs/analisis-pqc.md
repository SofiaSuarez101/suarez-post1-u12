# Impacto de la computación cuántica en la seguridad de los sistemas de información

**Arquitectura de Computadores · Unidad 12 · Post-contenido (Parte 2)**
**Documento técnico de análisis — criptografía post-cuántica (PQC)**

---

## Resumen

Este documento analiza el efecto de la computación cuántica sobre la criptografía en uso y evalúa los tres estándares post-cuánticos publicados por el NIST en agosto de 2024 (FIPS 203, 204 y 205). Se clasifican los algoritmos actuales según su vulnerabilidad al algoritmo de Shor o de Grover, se cuantifica el crecimiento de claves, ciphertexts y firmas frente a la criptografía clásica, se estima el impacto sobre un handshake TLS 1.3 híbrido y se formula un plan de migración para tres perfiles organizacionales con horizontes de sensibilidad distintos. El documento cierra con cuatro decisiones técnicas justificadas (dos de ellas, las de los Pasos 5 y 6, específicas de esta parte).

---

## 1. Inventario de algoritmos criptográficos vulnerables

El algoritmo de Shor (Shor, 1994) resuelve en tiempo polinomial la factorización de enteros y el logaritmo discreto, incluidos los de curvas elípticas. Con ello, la seguridad de RSA, DH/ECDH y ECDSA/EdDSA desaparece por completo si existe un computador cuántico criptográficamente relevante (CRQC). El algoritmo de Grover (Grover, 1996) ofrece una aceleración cuadrática en la búsqueda no estructurada, de modo que reduce a la mitad, en bits, la seguridad de los esquemas simétricos y de hash; este efecto se compensa duplicando el tamaño de clave o de salida.

| Algoritmo | Tipo | Vulnerabilidad cuántica | Algoritmo atacante | Acción post-cuántica |
|---|---|---|---|---|
| RSA-2048 / RSA-4096 | Asimétrico (cifrado / firma / transporte de clave) | **Roto completamente** | Shor (factorización, tiempo polinomial) | Reemplazar: ML-KEM (transporte de clave), ML-DSA / SLH-DSA (firma) |
| ECDSA (P-256, P-384) | Firma digital | **Roto completamente** | Shor (logaritmo discreto en curvas elípticas) | Reemplazar con ML-DSA (o SLH-DSA como respaldo) |
| ECDH / X25519 | Intercambio de clave | **Roto completamente** | Shor (logaritmo discreto) | Reemplazar con ML-KEM (en modo híbrido durante la transición) |
| AES-128 | Cifrado simétrico | **Debilitado** (≈ 64 bits de seguridad teórica frente a Grover) | Grover, O(√N) | Migrar a AES-256 |
| AES-256 | Cifrado simétrico | **Aceptable** (≈ 128 bits efectivos) | Grover, O(√N) | Mantener |
| SHA-256 | Función hash | **Debilitada** (preimagen: 2²⁵⁶ → 2¹²⁸; colisiones: cota teórica de 2¹²⁸ a ≈ 2⁸⁵ con BHT) | Grover / Brassard-Høyer-Tapp | Migrar a SHA-384/512 donde se requiera margen post-cuántico |
| SHA-3-256 | Función hash | **Debilitada**, equivalente a SHA-256 | Grover | Usar SHA3-384 o superior |

**Distinción clave.** "Roto completamente" significa que la seguridad del esquema se pierde por completo, lo que compromete retroactivamente la confidencialidad de cualquier tráfico capturado antes de la migración (amenaza HNDL, *harvest now, decrypt later*). "Debilitado" significa que el margen de seguridad se reduce, pero el esquema sigue siendo útil si se ajusta el parámetro (clave o salida más larga).

**Matices técnicos.** Dos precisiones evitan sobrestimar la amenaza de Grover. Primero, el ataque de Grover requiere una ejecución secuencial profunda y se paraleliza mal, por lo que el NIST sigue considerando AES-128 aceptable (categoría 1 de seguridad) y la recomendación de AES-256 es una medida de margen, no una ruptura. Segundo, la cota de 2⁸⁵ para colisiones en SHA-256 es un resultado teórico de consumo de memoria cuántica poco realista, y el consenso es que los hash no representan el riesgo principal frente a la computación cuántica.

> **Checkpoint 1.** La tabla clasifica 7 algoritmos, separa vulnerables a Shor (asimétricos) de vulnerables a Grover (simétricos y hash), indica la remediación y distingue "roto" de "debilitado".

---

## 2. Estándares NIST PQC 2024: análisis comparativo

En agosto de 2024 el NIST publicó los tres primeros estándares federales de criptografía post-cuántica (NIST, 2024a; 2024b; 2024c).

### 2.1 ML-KEM (FIPS 203, derivado de CRYSTALS-Kyber)

Es un mecanismo de encapsulamiento de claves (KEM) cuya seguridad se apoya en el problema **Module Learning With Errors (MLWE)**. No cifra mensajes arbitrarios: permite que dos partes acuerden un secreto compartido de 32 bytes. **Reemplaza a ECDH/X25519 y al transporte de clave con RSA.**

| Conjunto | Clave pública (encapsulación) | Clave privada (decapsulación) | Ciphertext | Secreto compartido | Categoría NIST |
|---|---|---|---|---|---|
| ML-KEM-512 | 800 B | 1632 B | 768 B | 32 B | 1 (≈ AES-128) |
| ML-KEM-768 | 1184 B | 2400 B | 1088 B | 32 B | 3 (≈ AES-192) |
| ML-KEM-1024 | 1568 B | 3168 B | 1568 B | 32 B | 5 (≈ AES-256) |

*Fuente: NIST (2024a), FIPS 203, Sección 8. Los tamaños cumplen las fórmulas del estándar: clave pública = 384k + 32 B, clave privada = 768k + 96 B y ciphertext = 32(dᵤ·k + dᵥ) B, con k = 2, 3 y 4.*

### 2.2 ML-DSA (FIPS 204, derivado de CRYSTALS-Dilithium)

Es un esquema de firma digital basado en retículos (MLWE y SIS modulares, con la técnica "Fiat-Shamir con abortos"). **Reemplaza a ECDSA y a las firmas RSA.**

| Conjunto | Clave pública | Clave privada | Firma | Categoría NIST |
|---|---|---|---|---|
| ML-DSA-44 | 1312 B | 2560 B | 2420 B | 2 |
| ML-DSA-65 | 1952 B | 4032 B | 3309 B | 3 |
| ML-DSA-87 | 2592 B | 4896 B | 4627 B | 5 |

*Fuente: NIST (2024b), FIPS 204. Cifras verificadas también en la tabla de tamaños de la RFC 9964 (IETF, 2026), que cita FIPS 204.*

Frente a ECDSA P-256 (clave pública de 64 B y firma de ≈ 72 B en DER), ML-DSA-65 multiplica por ≈ 30 la clave pública y por ≈ 46 la firma. A cambio, sus operaciones de firma y verificación son rápidas, del mismo orden que las de ECC en implementaciones optimizadas.

### 2.3 SLH-DSA (FIPS 205, derivado de SPHINCS+)

Es un esquema de firma **basado únicamente en funciones hash** (árboles de Merkle, WOTS+ y FORS). Su seguridad depende solo de la resistencia a colisiones y a preimagen de la función hash subyacente, sin asumir la dificultad de ningún problema algebraico estructurado. Por eso es la opción **más conservadora** en sus asunciones: si en el futuro se descubriera un ataque contra los retículos estructurados, SLH-DSA no se vería afectado.

| Conjunto (variante SHA2 / SHAKE) | Clave pública | Clave privada | Firma | Categoría NIST |
|---|---|---|---|---|
| SLH-DSA-128s (pequeña, lenta) | 32 B | 64 B | 7856 B | 1 |
| SLH-DSA-128f (rápida, grande) | 32 B | 64 B | 17 088 B | 1 |

*Fuente: NIST (2024c), FIPS 205. El tamaño de firma sigue la fórmula (1 + k(1 + a) + h + d·len)·n del estándar; para 128s resulta 491 × 16 = 7856 B.*

El precio de ese conservadurismo es el tamaño de la firma (varios KB) y, sobre todo, la velocidad de firma, muy inferior a la de ML-DSA. Se recomienda como **respaldo de diversidad criptográfica** y para activos de vida muy larga con baja frecuencia de firma (raíces de PKI, firmware).

### 2.4 Velocidad relativa

Los documentos FIPS no publican *benchmarks*, porque el rendimiento depende de la implementación y de la plataforma. De forma cualitativa, y consistente con la literatura de los equipos de diseño: ML-KEM y ML-DSA son comparables a ECC en latencia de operación (microsegundos a decenas de microsegundos en CPU moderna), mientras que SLH-DSA firma entre uno y dos órdenes de magnitud más lento que ML-DSA, aunque su verificación sigue siendo rápida. Quien reproduzca este análisis puede medir cifras propias con `speed_sig` y `speed_kem` de liboqs (Open Quantum Safe, s. f.).

### 2.5 Qué reemplaza a qué

| Función actual | Algoritmo vulnerable | Reemplazo estandarizado |
|---|---|---|
| Intercambio / encapsulamiento de clave | ECDH, X25519, RSA-KEM | **ML-KEM** (FIPS 203) |
| Firma digital | ECDSA, RSA-PSS | **ML-DSA** (FIPS 204), con **SLH-DSA** (FIPS 205) como respaldo |

El NIST seleccionó además a HQC como KEM de respaldo en 2025 y trabaja en FN-DSA (basado en Falcon, futuro FIPS 206), lo que refuerza la recomendación de diseñar los sistemas con **agilidad criptográfica**.

> **Checkpoint 2.** La sección contiene la tabla de tamaños en bytes de los tres estándares, cita la fuente de cada cifra, y explica que ML-KEM reemplaza a ECDH/RSA como KEM, mientras que ML-DSA y SLH-DSA reemplazan a ECDSA/RSA en firmas.

---

## 3. Plan de migración para tres perfiles organizacionales

### 3.1 Principios comunes

1. **Inventariar primero.** No se puede migrar lo que no se conoce: se cataloga cada uso de criptografía asimétrica (TLS, VPN, SSH, PKI, firma de código, firma de documentos, correo, bases de datos cifradas, HSM y dispositivos embebidos).
2. **Priorizar por la regla de Mosca.** Si *X* (años de vida útil requerida del dato) + *Y* (años de migración) > *Z* (años hasta un CRQC), la organización ya está en riesgo. Los datos con *X* grande exigen actuar primero.
3. **Confidencialidad antes que autenticidad.** La amenaza HNDL afecta a lo que se cifra hoy y se guardará mucho tiempo; una firma solo puede falsificarse una vez que existe el CRQC.
4. **Híbrido en la transición.** Se combina un algoritmo clásico con uno PQC en paralelo, de modo que la conexión sea segura si cualquiera de los dos resiste.
5. **Agilidad criptográfica.** Los algoritmos se parametrizan y se abstraen en bibliotecas o configuración, no se fijan en el código.

### 3.2 Perfil A: hospital universitario (sensibilidad de 50 a 75 años)

**Contexto.** Historias clínicas con horizonte de 50 a 75 años, portal de pacientes bajo TLS y firma de prescripciones con ECDSA. La amenaza HNDL es **crítica**: el tráfico interceptado hoy puede descifrarse en 10 a 15 años, cuando los datos siguen siendo sensibles.

**1. Inventario de sistemas con criptografía asimétrica activa.** Portal de pacientes (TLS con ECDHE y ECDSA/RSA), VPN entre sedes, interfaces de interoperabilidad clínica (HL7/FHIR sobre TLS), PKI interna y firma de prescripciones (ECDSA), correo seguro, copias de seguridad cifradas con envoltura de clave RSA y dispositivos médicos con certificados de larga vida.

**2. Clasificación por horizonte de sensibilidad.**

| Dato | Horizonte | Riesgo dominante |
|---|---|---|
| Historia clínica y comunicaciones del portal | 50-75 años | HNDL (confidencialidad) |
| Copias de seguridad cifradas | 50-75 años | HNDL si la clave se envuelve con RSA/ECC |
| Prescripciones firmadas | Autenticidad en el momento de emisión y auditoría legal | Falsificación futura (menor) |
| Telemetría operativa | Meses a pocos años | Bajo |

**3. Estrategia híbrida.** El TLS del portal pasa de inmediato a intercambio de clave híbrido **X25519MLKEM768**. En VPN y en el envoltorio de claves de las copias de seguridad se combina ECDH con ML-KEM-768 (o ML-KEM-1024 para el repositorio de archivo de más larga vida). Los datos en reposo ya usan AES-256, que se mantiene. Las prescripciones se firman con **ML-DSA-65** (véase la decisión técnica del Paso 5), con doble firma ECDSA + ML-DSA durante la transición para no romper a los verificadores existentes.

**4. Cronograma.**

| Fase | Periodo | Hito verificable |
|---|---|---|
| 0. Inventario y priorización | Mes 0-3 | Catálogo criptográfico (CBOM) completo, con cada activo etiquetado por horizonte de sensibilidad |
| 1. Confidencialidad en el perímetro | Mes 3-9 | Portal de pacientes y VPN negociando X25519MLKEM768 en ≥ 95 % de las sesiones (medido en logs del balanceador) |
| 2. Re-envoltura de claves de archivo | Mes 6-18 | Claves de copias de seguridad re-envueltas con ML-KEM; AES-256 verificado en todo el almacenamiento |
| 3. Firma de prescripciones y PKI | Mes 12-30 | Emisión con doble firma ECDSA + ML-DSA-65; PKI interna con jerarquía PQC piloto |
| 4. Retiro del material clásico | Mes 30-48 | Verificadores actualizados; ECDSA/RSA retirados de los flujos de firma nuevos |

**5. Riesgos y mitigaciones.**

- *Dispositivos médicos que no pueden actualizarse:* segmentación de red y *proxy* de terminación TLS PQC delante del dispositivo.
- *Tamaño de firmas y certificados:* medir latencia en el portal y habilitar compresión y caché de certificados.
- *Implementaciones inmaduras:* usar bibliotecas validadas (por ejemplo, módulos con programa de validación CMVP) y mantener pruebas de interoperabilidad.
- *Agilidad insuficiente en software heredado:* exigir cláusulas de agilidad criptográfica a los proveedores.

### 3.3 Perfil B: startup de comercio electrónico (sensibilidad de 5 a 7 años)

**Contexto.** Transacciones con AES-256 y TLS 1.3 (X25519 + ECDSA) y datos de tarjeta bajo PCI-DSS, con vida útil de 5 a 7 años. La urgencia es menor que en salud, pero el soporte de TLS híbrido para clientes es un diferenciador competitivo temprano y su costo es bajo.

**1. Inventario.** Terminación TLS en CDN o balanceador, API de pagos, TLS hacia el procesador de pagos, certificados de servidor (ECDSA), firma de código y de artefactos de CI/CD, JWT firmados y VPN de administración.

**2. Clasificación.** Datos de tarjeta y transacciones: 5-7 años (HNDL moderado). Datos de cuenta de usuario: 5-10 años. Tokens de sesión: minutos a horas (sin riesgo HNDL relevante).

**3. Estrategia híbrida.** Se habilita **X25519MLKEM768** en el borde (CDN o balanceador) sin cambiar la cadena de certificados, que sigue siendo ECDSA en esta etapa. Se prueban certificados PQC en entornos internos. Se mantiene AES-256 y se migra de SHA-256 a SHA-384 donde convenga.

**4. Cronograma.**

| Fase | Periodo | Hito verificable |
|---|---|---|
| 0. Inventario | Mes 0-2 | Lista de endpoints TLS y dependencias de terceros |
| 1. KEM híbrido en el borde | Mes 2-6 | Porcentaje de handshakes híbridos ≥ 70 % (clientes modernos) sin aumento significativo de errores ni de latencia p95 |
| 2. Proveedores y procesador de pagos | Mes 6-18 | Evidencia contractual de hoja de ruta PQC de los proveedores críticos |
| 3. Certificados y firma internos | Mes 18-36 | Certificados ML-DSA en entorno interno y firma de artefactos con doble firma |
| 4. Evaluación de simplificación | Mes 36-60 | Decisión documentada sobre pasar a PQC puro según madurez y regulación |

**5. Riesgos y mitigaciones.**

- *Middleboxes que rompen ClientHello grandes:* pruebas de interoperabilidad y *fallback* controlado a X25519.
- *Dependencia de la hoja de ruta de terceros (adquirentes, PCI):* seguimiento de las guías del PCI SSC.
- *Latencia en redes móviles:* medición continua por segmento de red.

### 3.4 Perfil C: entidad gubernamental de defensa (sensibilidad de 25 a 50 años)

**Contexto.** Comunicaciones clasificadas, firma de documentos oficiales (PKI nacional) y VPN entre agencias, con vida útil de 25 a 50 años. La migración es **mandatoria** bajo la guía CNSA 2.0 de la NSA (2022), con plazos escalonados entre 2025 y 2033 (NSA, 2022).

**1. Inventario.** PKI nacional (raíces e intermedias), VPN IPsec entre agencias, TLS interno, firma de firmware y de software, firma de documentos oficiales, enlaces de comunicaciones cifrados, módulos HSM y sistemas embebidos con ciclos de vida de décadas.

**2. Clasificación.** Material clasificado y claves raíz: 25-50 años o más (HNDL y falsificación futura). Firma de firmware: vida del equipo, por lo que **la firma de código es prioritaria** porque un equipo desplegado no puede actualizarse fácilmente.

**3. Estrategia.** CNSA 2.0 selecciona **ML-KEM-1024** para establecimiento de claves, **ML-DSA-87** para firma, AES-256 y SHA-384/512, y esquemas de firma basados en hash con estado (LMS/XMSS) para firma de software y firmware. La NSA no exige el modo híbrido como requisito, aunque puede admitirse por interoperabilidad mientras convivan sistemas de distintas fases. La entidad adopta híbrido solo en enlaces con socios que aún no soportan PQC puro, y diseña el resto hacia PQC puro.

**4. Cronograma (alineado con CNSA 2.0).**

| Fase | Periodo | Hito verificable |
|---|---|---|
| 0. Inventario y CBOM | 2026 | Catálogo completo de activos con criptografía asimétrica y fecha objetivo por sistema |
| 1. Firma de software y firmware | 2025-2030 | Toda firma nueva de código/firmware con LMS/XMSS o ML-DSA-87; soporte y preferencia PQC desde 2025 |
| 2. Equipos de red y VPN | 2026-2030 | VPN y equipos de red con ML-KEM-1024; uso exclusivo de CNSA 2.0 hacia 2030 |
| 3. Navegadores, servidores y servicios en la nube | 2025-2033 | TLS con ML-KEM-1024 como preferido y luego exclusivo hacia 2033 |
| 4. Sistemas operativos, equipos específicos y heredados | 2027-2033 | Reemplazo o aislamiento de lo que no pueda migrar antes de 2033 |

**5. Riesgos y mitigaciones.**

- *Plazos fijos con cadenas de suministro lentas:* exigir hojas de ruta PQC a proveedores con penalizaciones contractuales.
- *Firmas con estado (LMS/XMSS):* una reutilización de estado rompe la seguridad, por lo que se gestiona el estado en HSM con procedimientos auditados.
- *Equipos de larga vida sin actualización:* sustitución programada y aislamiento de red.

> **Checkpoint 3.** Los tres perfiles incluyen inventario, clasificación por horizonte, estrategia híbrida o PQC según el caso, cronograma con al menos 3 hitos verificables, y riesgos con mitigaciones. La priorización sigue el horizonte de sensibilidad: A (confidencialidad inmediata) > C (plazo regulatorio) > B (estrategia oportunista de bajo costo).

---

## 4. Tamaños de clave y firma: PQC frente a criptografía clásica, e impacto en TLS 1.3 híbrido

### 4.1 Tabla comparativa

| Algoritmo | Tipo | Clave pública | Clave privada | Firma / ciphertext | Nivel de seguridad |
|---|---|---|---|---|---|
| RSA-3072 | Cifrado/firma clásico | ≈ 384 B (módulo; ≈ 390-400 B en DER) | ≈ 1600-2400 B (según codificación) | 384 B (firma) | ≈ 128 bits clásicos (no post-cuántico) |
| ECDSA P-256 | Firma clásica | 64 B | 32 B | ≈ 70-72 B (DER) | ≈ 128 bits clásicos (no post-cuántico) |
| X25519 | Intercambio de clave clásico | 32 B | 32 B | N/A (KEX) | ≈ 128 bits clásicos (no post-cuántico) |
| ML-KEM-768 (FIPS 203) | KEM post-cuántico | 1184 B | 2400 B | 1088 B (ciphertext) | Nivel NIST 3 (≈ AES-192) |
| ML-DSA-65 (FIPS 204) | Firma post-cuántica | 1952 B | 4032 B | 3309 B | Nivel NIST 3 (≈ AES-192) |
| SLH-DSA-128s (FIPS 205) | Firma post-cuántica (hash) | 32 B | 64 B | 7856 B | Nivel NIST 1 (≈ AES-128) |

*Fuentes: NIST (2024a, 2024b, 2024c) para las filas PQC; las filas clásicas provienen de los parámetros estándar de cada algoritmo (la clave privada y la codificación DER de RSA varían con el formato).*

**Factores de crecimiento calculados:**

- Clave pública de ML-KEM-768 frente a X25519: 1184 / 32 = **37×**.
- Firma de ML-DSA-65 frente a ECDSA P-256: 3309 / 72 ≈ **46×**.
- Firma de SLH-DSA-128s frente a ECDSA P-256: 7856 / 72 ≈ **109×**.
- Firma de ML-DSA-65 frente a RSA-3072: 3309 / 384 ≈ **8,6×**.

### 4.2 Impacto en un handshake TLS 1.3 híbrido X25519 + ML-KEM-768

El intercambio de clave híbrido se negocia como el grupo **X25519MLKEM768** (anteriormente desplegado como X25519Kyber768Draft00 por Chrome y Cloudflare). Los campos `key_share` crecen así:

| Mensaje | Solo X25519 | Híbrido X25519 + ML-KEM-768 | Aumento |
|---|---|---|---|
| ClientHello (`key_share`) | 32 B | 32 + 1184 = **1216 B** | +1184 B (≈ 38×) |
| ServerHello (`key_share`) | 32 B | 32 + 1088 = **1120 B** | +1088 B (≈ 35×) |

El aumento total del intercambio es de **≈ 2,3 KB**. Con una ventana de congestión inicial típica de TCP de 10 segmentos (≈ 14,6 KB con MSS de 1460 B), el ClientHello de ≈ 1,2 KB más el resto de extensiones suele caber en uno o dos segmentos, por lo que **en el caso común el híbrido no añade rondas de red**. Las implementaciones desplegadas reportan este comportamiento.

**Efecto de una cadena de certificados con ML-DSA.** Si, además del intercambio híbrido, se autentica con ML-DSA-65, aparecen tres firmas (certificado hoja, certificado intermedio y `CertificateVerify`) y dos claves públicas. La estimación solo de esos campos (sin otros datos del certificado ni SCTs) es:

| Autenticación | Cálculo | Total aproximado |
|---|---|---|
| ECDSA P-256 | 3 × 72 B (firmas) + 2 × 64 B (claves) | ≈ **344 B** |
| ML-DSA-65 | 3 × 3309 B (firmas) + 2 × 1952 B (claves) | ≈ **13 831 B** |

El resultado, ≈ 13,8 KB frente a ≈ 0,3 KB (unas 40 veces más), se acerca al tamaño de la ventana inicial de congestión (≈ 14,6 KB). Sumado el resto del handshake, es probable que los datos se fragmenten en más segmentos y, **en redes con alta latencia o pérdida de paquetes, requieran una ronda adicional** que aumenta la latencia percibida. Por eso se recomienda: (1) desplegar primero el KEM híbrido, que aporta protección contra HNDL con costo mínimo; (2) retrasar los certificados PQC hasta contar con mitigaciones (compresión de certificados, omisión de intermedios, nuevos formatos de certificado); y (3) medir en el entorno real.

> **Checkpoint 4.** La tabla incluye los seis algoritmos con tamaños en bytes y fuentes; el cálculo del `key_share` híbrido (1216 B y 1120 B) está explicado y se detallan las condiciones en que se añaden o no rondas de red.

---

## 5. Decisión técnica: ¿qué algoritmo NIST firma las prescripciones del Perfil A?

**Decisión: ML-DSA-65 como algoritmo principal, con SLH-DSA como respaldo para activos de larga vida.**

En primer lugar, **ML-KEM queda descartado de entrada**, porque es un mecanismo de encapsulamiento de claves (acuerda un secreto compartido) y no un esquema de firma; no ofrece autenticidad ni no repudio. Firmar una prescripción exige un esquema de firma digital, así que la elección real es entre ML-DSA y SLH-DSA.

Entre ambos, los datos del Paso 4 favorecen a **ML-DSA-65**: su firma ocupa 3309 B frente a 7856 B de SLH-DSA-128s (≈ 2,4× menos) y, sobre todo, firma y verifica mucho más rápido. Para un hospital que emite miles de prescripciones por día con un portal de baja latencia, el tamaño de la firma afecta el almacenamiento y la transmisión, y la lentitud de firma de SLH-DSA afectaría la experiencia del usuario y el rendimiento del servidor.

El argumento a favor de SLH-DSA es su asunción de seguridad más conservadora (solo depende de la resistencia del hash, sin asumir la dificultad de MLWE). Sin embargo, ese argumento pesa menos en este caso. La amenaza HNDL aplica a la **confidencialidad** de datos cifrados que se guardan durante décadas; no aplica de la misma forma a la **autenticidad** de una firma, cuyo propósito es probar quién emitió la prescripción en el momento de emitirla, y que solo podría falsificarse cuando exista un computador cuántico capaz de romper el esquema. El horizonte de 50 a 75 años del Perfil A rige, por tanto, la elección del KEM del portal (híbrido con ML-KEM desde ahora), no la del algoritmo de firma. Además, durante la transición se recomienda **doble firma ECDSA + ML-DSA-65** y se reserva **SLH-DSA** (diversidad criptográfica) para certificados raíz o de larga vida, donde la conservadurismo pesa más que el rendimiento y la frecuencia de firma es baja. La agilidad criptográfica permite sustituir ML-DSA por otro algoritmo si en el futuro se debilitara.

---

## 6. Decisión técnica: ¿modo híbrido permanente o etapa de transición para el Perfil B?

**Decisión: adoptar el modo híbrido (X25519 + ML-KEM-768) desde ahora, entendido como etapa de transición y no como estado permanente.**

El análisis del Paso 4 muestra que el sobrecosto del KEM híbrido es pequeño: ≈ 2,3 KB adicionales en el intercambio, que en el caso común cabe en la ventana inicial de TCP y no agrega rondas de red. Con ese costo bajo, el beneficio justifica adoptarlo ya, y no esperar a que la migración sea obligatoria: el Perfil B gana protección frente a HNDL para datos de 5 a 7 años y ofrece compatibilidad temprana con navegadores y CDNs que ya negocian el híbrido por defecto.

El híbrido protege contra dos fallas **no correlacionadas**: (1) que ECC sea roto por un computador cuántico suficientemente grande, y (2) que ML-KEM o ML-DSA, estandarizados en 2024 y con muchos menos años de escrutinio público que ECC (décadas), tengan una debilidad clásica aún no descubierta. Esa doble protección es especialmente valiosa mientras los algoritmos PQC acumulan años de análisis criptográfico, porque la ruptura de uno de los dos componentes no compromete la sesión.

Sin embargo, el híbrido tiene un costo permanente en bytes, complejidad de implementación y superficie de ataque (dos algoritmos que mantener). Por ello conviene planearlo como **puente**: cuando ML-KEM y ML-DSA acumulen confianza y adopción, y los plazos regulatorios (por ejemplo CNSA 2.0 hacia 2033) maduren, el Perfil B puede simplificar hacia PQC puro. Como su exigencia regulatoria y su horizonte de datos son menores que los del Perfil C, puede hacerlo más tarde y con menor urgencia, tras una evaluación documentada en la fase 4 de su cronograma.

> **Checkpoint 5.** Las dos decisiones técnicas (Pasos 5 y 6) están incluidas en este documento y superan las 100 palabras cada una.

---

## 7. Conclusiones

1. La computación cuántica rompe por completo la criptografía asimétrica actual (RSA, ECDH, ECDSA) mediante el algoritmo de Shor, y debilita sin romper a la simétrica y a los hash mediante el algoritmo de Grover; los remedios son, respectivamente, reemplazar por PQC y aumentar el tamaño de clave o de salida.
2. El NIST estandarizó ML-KEM (FIPS 203) para el intercambio de claves, y ML-DSA (FIPS 204) y SLH-DSA (FIPS 205) para firmas, con ML-DSA como opción general y SLH-DSA como respaldo conservador.
3. El costo principal de la migración es el tamaño: claves públicas y firmas 30 a 110 veces mayores que las de ECC. El KEM híbrido tiene un impacto pequeño en TLS, mientras que las cadenas de certificados PQC pueden añadir rondas de red en enlaces de alta latencia.
4. La prioridad de migración la define el horizonte de sensibilidad de los datos: confidencialidad de larga vida primero (Perfil A), plazos regulatorios (Perfil C) y adopción oportunista de bajo costo (Perfil B).
5. La agilidad criptográfica es la medida de mayor valor a largo plazo: permite cambiar de algoritmo sin rediseñar los sistemas.

---

## Referencias (APA 7)

Grover, L. K. (1996). A fast quantum mechanical algorithm for database search. *Proceedings of the 28th Annual ACM Symposium on Theory of Computing*, 212-219. https://doi.org/10.1145/237814.237866

National Institute of Standards and Technology. (2024a). *Module-lattice-based key-encapsulation mechanism standard* (FIPS PUB 203). U.S. Department of Commerce. https://doi.org/10.6028/NIST.FIPS.203

National Institute of Standards and Technology. (2024b). *Module-lattice-based digital signature standard* (FIPS PUB 204). U.S. Department of Commerce. https://doi.org/10.6028/NIST.FIPS.204

National Institute of Standards and Technology. (2024c). *Stateless hash-based digital signature standard* (FIPS PUB 205). U.S. Department of Commerce. https://doi.org/10.6028/NIST.FIPS.205

National Security Agency. (2022). *Commercial National Security Algorithm Suite 2.0* (Cybersecurity advisory). https://media.defense.gov/2022/Sep/07/2003071834/-1/-1/0/CSA_CNSA_2.0_ALGORITHMS_.PDF

Open Quantum Safe. (s. f.). *liboqs: C library for prototyping and experimenting with quantum-resistant cryptography*. https://openquantumsafe.org/liboqs/

Internet Engineering Task Force. (2026). *ML-DSA for JOSE and COSE* (RFC 9964). RFC Editor. https://www.rfc-editor.org/rfc/rfc9964

Shor, P. W. (1994). Algorithms for quantum computation: Discrete logarithms and factoring. *Proceedings of the 35th Annual Symposium on Foundations of Computer Science*, 124-134. https://doi.org/10.1109/SFCS.1994.365700

*Pendiente antes de entregar:* si se consultan la guía CISA/NSA/NIST (2023) y ETSI GR QSC 006 mencionadas en el enunciado, agregarlas aquí en formato APA con los datos del documento que se haya leído.
