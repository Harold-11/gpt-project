# Dimensiones y decisiones de la primera versión

Todas las dimensiones son supuestas: no se dispone de una medida física, escala fotográfica ni vistas laterales, posterior o inferior confirmadas.

| Parte | Valor asumido | Cómo se decidió |
|---|---:|---|
| Ancho exterior | 90 cm | Proporción rectangular alargada de la imagen |
| Fondo exterior | 55 cm | Relación visual ancho/fondo aproximada |
| Altura exterior | 18 cm | Frente grueso visible |
| Abertura superior de la poza | 56 × 31 cm | Rectángulo integrado de la referencia |
| Fondo de la poza | 45 × 20 cm | Reducción que produce las paredes inclinadas |
| Profundidad desde el borde al fondo periférico | 12 cm | Estimación visual |
| Caída adicional hacia el desagüe | 6 mm | Decisión de reconstrucción, no medida |
| Espesor mínimo de piedra bajo el fondo | 5,4 cm aproximadamente | Diferencia entre altura y profundidad máxima |
| Desagüe | Ø 4,5 cm | Estimación; sin aro metálico |
| Posición del desagüe | X = −11 cm; Z = 0 | Desplazado a la izquierda de la poza como en la referencia |
| Centro de la poza | X = +3,5 cm; Z = −1,2 cm | Ligera asimetría visual de la referencia |
| Bisel exterior | 1,5 mm | Suavizado visual mínimo para captar reflejos |
| Radio de esquinas interiores | 3–8 mm según altura | Pequeño suavizado estimado; conserva aspecto rectangular |
| Cara inferior | Plana y cerrada salvo el desagüe | No visible en la imagen; solución explícitamente estimada |
| Conducto del desagüe | Cilíndrico hasta la cara inferior | No visible; solución estimada |
| Agujero en borde posterior | Omitido | No confirmado en el producto original |

La forma de las paredes se reconstruyó como cuatro planos inclinados con pequeñas transiciones en las esquinas. La textura y el acabado satinado se generaron con código, no se proyectó la foto sobre una caja. El moteado y el tono se ajustaron visualmente; no son un escaneo ni una medición del material.

## Pendiente del fondo

El borde del fondo está 12 cm por debajo del plano superior. El borde del orificio está 12,6 cm por debajo. Hay una transición radial suave con caída hacia el desagüe. No se ha calculado capacidad hidráulica, espesor estructural ni compatibilidad con herrajes: deberán revisarse con medidas reales antes de fabricar.

## Lista para una segunda versión

1. Medir ancho, fondo, altura, abertura, profundidad, diámetro y posición del desagüe.
2. Confirmar forma inferior y espesor real de piedra.
3. Revisar si existe perforación para grifería en el producto original.
4. Ajustar `dimensions.json`, regenerar y comparar con fotografías frontal/superior/lateral.
5. Tras aprobar la forma, integrar el mismo GLB en la animación por scroll.
