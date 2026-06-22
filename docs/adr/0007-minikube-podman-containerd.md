# 0007 — Driver de minikube: podman con --container-runtime=containerd

- Estado: Aceptada
- Fecha: 2026-06-22
- Contexto: Elegir un runtime local de Kubernetes que funcione.

## Contexto y problema

El entorno de desarrollo es macOS con podman (sin daemon de Docker).
`minikube start` por default usa el driver docker en macOS, que no
funciona acá. El driver podman es la elección natural pero tiene
problemas conocidos de compatibilidad con el `--container-runtime=cri-dockerd`
por default dentro de la VM de minikube.

## Qué probamos

| Intento | Resultado |
|---|---|
| `minikube start --driver=podman` (defaults) | `apiserver: Stopped`. El kubelet no lograba arrancar los static pods (`kube-apiserver`, `etcd`, etc.) por errores de `RLIMIT_NPROC` desde runc. |
| `hostNetwork: true` en CoreDNS para saltar la red de pods | CoreDNS crasheó: `bind: permission denied` en `:53`. Otro proceso ya tenía ese puerto dentro de la VM de minikube. |
| Revertir y cambiar `--container-runtime=containerd` | Funcionó. El kubelet usa containerd directamente; el `cri-dockerd` interno y su wrapper de runc quedan fuera del camino. |

## Decisión

Usar `minikube start --driver=podman --container-runtime=containerd`.
Es la única combinación que produce un control plane funcional en este
entorno.

## Consecuencias

Bueno:
- Un clúster single-node reproducible desde estado limpio.
- El CNI (`kindnet`) queda contento porque containerd 2.x entiende
  los OCI image indexes que produce podman.

Malo / trade-offs:
- `cri-dockerd` es lo que usa la mayoría de los clústeres de
  producción. No estamos ejercitando ese camino. Si el diplomado apunta
  después a un clúster real que use `cri-dockerd` (EKS viejo, por
  ejemplo), habrá que estar atento a diferencias en mensajes de error
  de pull y en cómo se aplica `--seccomp-profile`.
- Dependemos de una imagen `kicbase` vieja en la cache local. Versiones
  más nuevas de minikube traen imágenes más frescas.
