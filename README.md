# Lavadero de piedra — modelo 3D paramétrico

Primera aproximación visual propia, construida mediante código a partir de una sola imagen de referencia. No se utilizó el modelo de Tripo ni su geometría. El objetivo es revisar el producto en 3D y disponer de un GLB ligero para una futura web.

## Entregables

- `dist/lavadero-piedra.glb`: modelo glTF 2.0 binario con dos texturas incluidas. Una malla, un material, 4.550 triángulos; 620.156 bytes.
- `dist/lavadero-vista-3d.html`: visor autónomo con Three.js, OrbitControls, el GLB y sus texturas incorporados. Abrir en un navegador con WebGL 2. No usa CDN, no necesita internet, instalación ni servidor. Algunas vistas previas de archivos en móviles no ejecutan JavaScript; en ese caso abrir el HTML en un navegador compatible.
- `src/generate_model.py`: generador de geometría, textura y GLB.
- `dimensions.json`: dimensiones en metros y parámetros editables.
- `src/viewer.js`, `src/viewer.template.html`, `src/build_preview.mjs`: fuente del visor y empaquetado.
- `dist/*validation.json`: informes de comprobación.
- `docs/DIMENSIONES-Y-ESTIMACIONES.md`: decisiones de reconstrucción y limitaciones.

## Regenerar

Requiere Python 3.12 o superior y Node.js 22 o superior. Se puede ejecutar completamente en Codex Cloud, GitHub Actions u otro servidor; no depende de carpetas ni aplicaciones del ordenador del propietario.

```sh
python -m venv .venv
# Linux / macOS:
. .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm ci
npm run build
npm run test:geometry
npm run test:gltf
npx playwright install --with-deps chromium --only-shell
npm run test:viewer
```

Editar `dimensions.json` y repetir `npm run build`. La semilla fija permite reproducir la textura. La geometría no necesita Blender. Las texturas externas en `dist/` son copias de trabajo; el GLB ya contiene sus bytes y funciona por sí mismo.

El visor permite órbita libre, zoom, vistas superior/frontal/inferior, giro automático, malla, cotas, fondo oscuro, exposición, descarga del GLB y captura de pantalla. No se ha implementado animación por scroll ni integración con la tienda.

## Geometría y materiales

Ejes: X = ancho, Y = vertical, Z positivo = frente. Unidades glTF: metros. El origen está en el centro del volumen exterior. Dimensiones 0,90 × 0,55 × 0,18 m. Poza de 0,12 m, con 6 mm adicionales de caída al desagüe.

La pieza tiene un borde exterior biselado de 1,5 mm, laterales rectos, paredes de poza inclinadas, transición inferior pequeña y un conducto circular abierto que atraviesa la base. No hay agujero para grifería, accesorios, soportes ni mueble. La escena del GLB contiene solamente el lavadero: luces, fondo y plano de sombra existen únicamente en el visor.

Textura procedural de piedra crema con grano fino, sin vetas grandes. Color base sRGB JPEG 1024²; rugosidad PNG 1024² en el canal verde, metalicidad 0. Mapeado UV a escala aproximada de 30 cm por repetición. El moteado imita visualmente la referencia y no identifica una variedad real de piedra. Se han empleado normales de superficie controladas para conservar planos limpios y suavizar solamente los biseles.

## Validación

- Khronos glTF Validator: cero errores y cero advertencias.
- Apertura independiente con pygltflib y trimesh.
- Volumen de piedra cerrado y coherente, un componente, orientaciones correctas, sin triángulos degenerados.
- Rayos verticales comprueban profundidad de la poza, base bajo el fondo, desagüe pasante y borde trasero sin perforación.
- Carga real con Three.js en Chromium; descarga idéntica al GLB exportado; sin peticiones externas ni errores de JavaScript.
- Controles del visor y tamaño móvil revisados. Ver informes y capturas en `dist/`.

El cierre topológico describe el material sólido de piedra; no tapa la poza ni el conducto del desagüe. La referencia no aporta escala ni vista inferior: este modelo sirve para visualización y revisión, no como plano de fabricación.

## Git Flow

`main` conserva la base estable. `develop` es la rama de integración. El trabajo de esta versión se encuentra en `feature/stone-sink-model`, con un PR hacia `develop`. Las futuras funciones irán en `feature/...`; versiones revisadas en `release/...`; correcciones urgentes en `hotfix/...` cuando proceda. No se ha fusionado el modelo con `main`.

## Trabajo en la nube y continuidad

El código y los artefactos se guardan en el repositorio. El flujo de GitHub Actions puede regenerar, comprobar y empaquetar el modelo sin que el PC esté encendido. Si una sesión de Codex o sus créditos se interrumpen, abrir esta rama y leer `docs/CONTINUIDAD.md`. La renovación de créditos no garantiza la reanudación automática de una conversación.

## Licencias

Código del proyecto: MIT, según `LICENSE`. Three.js: MIT, con aviso incluido en `THIRD_PARTY_NOTICES.txt` y en el visor empaquetado. La imagen de referencia proporcionada por el usuario no se redistribuye en el repositorio.
