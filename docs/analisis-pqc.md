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


