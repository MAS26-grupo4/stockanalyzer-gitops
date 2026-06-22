# 0008 — Reglas iptables FORWARD para tráfico saliente de los pods

- Estado: Aceptada
- Fecha: 2026-06-22
- Contexto: Los pods no podían salir a internet dentro del clúster de
minikube.

## Contexto y problema

Tras un `minikube start --driver=podman --container-runtime=containerd`
limpio, el control plane levantó y el API server respondía. Los pods
arrancaban, pero:

- La resolución DNS se colgaba (`socket.gaierror: Temporary failure in
  name resolution`) para todo dominio, incluyendo `google.com`.
- Las conexiones TCP a IPs públicas (`8.8.8.8:53`, `1.1.1.1:53`,
  `192.168.2.1:53`) se colgaban desde dentro de los pods.
- La IP del Service `10.96.0.10` (CoreDNS) también se colgaba.

El nodo en sí sí llegaba a internet y resolvía DNS, así que el problema
estaba entre la red de pods y el nodo.

## Diagnóstico

Tres piezas de evidencia:

1. `minikube ssh -- sudo iptables -L FORWARD -n -v` mostraba
   `Chain FORWARD (policy DROP 14 packets, 735 bytes)`. Los intentos
   de conexión nuevos se dropeaban en la policy por defecto de la chain.
2. Las chains de Kubernetes (`KUBE-FORWARD`, `KUBE-SERVICES`,
   `KUBE-EXTERNAL-SERVICES`, `DOCKER-FORWARD`) corrían primero pero
   ninguna aceptaba los paquetes. Caían a la policy.
3. La chain `KUBE-FORWARD` de K8s solo acepta paquetes con la marca
   `0x4000`, que pone `KUBE-MARK-MASQ` en la tabla `nat`. Los pods
   masqueradeados por otra chain (en nuestro caso un `KIND-MASQ-AGENT`
   residual) nunca recibían esa marca y se dropeaban.

## Decisión

Insertar dos reglas al tope de la chain FORWARD para permitir tráfico
desde y hacia el CIDR de pods:

```sh
sudo iptables -I FORWARD 2 -s 10.244.0.0/16 -j ACCEPT
sudo iptables -I FORWARD 2 -d 10.244.0.0/16 -j ACCEPT
```

Y, más defensivamente, una regla para conexiones established/related en
la posición 1:

```sh
sudo iptables -I FORWARD 1 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
```

Estas reglas no son persistentes frente a `minikube stop && start`. Hay
que reaplicarlas en cada arranque del clúster. (Aceptable para el
diplomado. Un clúster real no tiene este problema porque su CNI y las
reglas de `kube-proxy` arrancan coherentes desde el inicio.)

## Consecuencias

Bueno:
- Los pods vuelven a llegar a internet. DNS funciona. La app puede
  llamar a `guce.yahoo.com` para yfinance.
- El fix es un one-liner que se puede convertir en un `minikube ssh --`
  en un Makefile o en un hook de post-start de minikube.

Malo / trade-offs:
- Las reglas bypasean la chain `KUBE-FORWARD` administrada por K8s.
  Van a dejar pasar cualquier tráfico al CIDR de pods, no solo el
  masqueradeado. Aceptable en un clúster single-node; no es lo que
  querés en un multi-node donde la NetworkPolicy debe seguir siendo
  la autoridad.
- La causa raíz (el `KIND-MASQ-AGENT` residual y la ruta
  `KUBE-MARK-MASQ` faltante) sigue ahí. No la arreglamos; la rodeamos.
