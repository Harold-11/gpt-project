# Continuidad

Objetivo: lavadero propio en GLB, construido con código desde una referencia. Repositorio: Harold-11/gpt-project. Git Flow: feature/stone-sink-model → develop; main permanece estable.

Implementado: generador Python, malla con poza y desagüe real, texturas incorporadas, visor HTML autónomo, informes de formato/topología y pruebas del visor. Dimensiones estimadas en dimensions.json y docs/DIMENSIONES-Y-ESTIMACIONES.md.

Para continuar: revisar la última versión del PR, ejecutar los comandos del README y ajustar parámetros según la revisión del propietario. No empezar integración con scroll hasta que se solicite. No recrear la geometría usando Tripo; no hay archivo exportado de Tripo.

Si se interrumpe una ejecución, regenerar `dist/` desde los fuentes. El HTML empaqueta todo lo necesario y no carga código desde CDNs. Los archivos de la PC del propietario no son necesarios.
