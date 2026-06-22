# 0010 — Auth vía PAT classic en CI/CD (no GITHUB_TOKEN)

- Estado: Aceptada
- Fecha: 2026-06-22
- Contexto: El GITHUB_TOKEN no tenía scope `write:packages` en esta
organización.

## Contexto y problema

GitHub Actions en una organización con plan gratuito no siempre le da al
`GITHUB_TOKEN` autogenerado scope suficiente para pushear imágenes de
contenedor a ghcr.io. El error que vimos fue:

```
denied: permission_denied: write_package
```

Incluso después de habilitar los toggles relevantes en la organización
y en el repo, el error persistió para nuestra org. Necesitábamos una
alternativa que funcionara para el diplomado.

## Opciones consideradas

1. Seguir troubleshootando los permisos a nivel organización. Es la
   solución real, pero fuera del alcance del diplomado y depende del
   acceso de un admin de la org.
2. Usar un fine-grained personal access token. Más limpio, pero los
   fine-grained tokens no exponen `Packages: Read and Write` en cuentas
   gratuitas; eso es feature de planes pagos.
3. Usar un classic personal access token con `read:packages` y
   `write:packages`. Funciona en cualquier cuenta. El token se guarda
   como secret del repo.

## Decisión

Opción 3. Un PAT classic de `amcorrea0` con exactamente los dos scopes
requeridos (`read:packages`, `write:packages`), expiración 90 días,
guardado como secret del repo con nombre `CR_PAT` en
`MAS26-grupo4/stockanalyzer-gitops`. El workflow lo referencia como
`${{ secrets.CR_PAT }}` en el step de `docker/login-action`.

## Consecuencias

Bueno:
- El diplomado puede demostrar un pipeline de CI/CD end-to-end sin
  esperar cambios de política a nivel organización.
- El PAT está scoped solo a packages; no puede leer ni modificar código.

Malo / trade-offs:
- Un PAT personal es un secreto compartido. Si la cuenta de
  `amcorrea0` se compromete, el atacante puede pushear imágenes. La
  blast radius se limita intencionalmente solo al push de paquetes.
- El PAT hay que rotarlo (a mano) cada 90 días. Hay que poner un
  reminder en el calendario o migrar a un fine-grained token cuando la
  organización tenga plan pago.
- El archivo `.env` que se commiteó por accidente durante el diplomado
  (atrapado por push protection de GitHub) expuso el primer PAT, que
  rotamos de inmediato. El nuevo PAT vive solo en el secret store de
  GitHub Actions y nunca se escribió a disco.

## Trabajo futuro

Cuando la organización pase a plan pago:

1. Emitir un fine-grained token owned por una cuenta bot, scoped solo
   al paquete `stockanalyzer-gitops` y al repo
   `MAS26-grupo4/stockanalyzer-gitops`.
2. Reemplazar las referencias a `secrets.CR_PAT` con el secret de ese
   token.
3. Revocar el PAT classic.
