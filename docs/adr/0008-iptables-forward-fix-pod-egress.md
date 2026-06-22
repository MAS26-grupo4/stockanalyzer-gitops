# 0008 — iptables FORWARD rules for pod egress

- Status: Accepted
- Date: 2026-06-22
- Context: Pods could not reach the internet inside the minikube cluster.

## Context and Problem Statement

After a clean `minikube start --driver=podman --container-runtime=containerd`,
the control plane came up and the API server answered. Pods started, but:

- DNS resolution timed out (`socket.gaierror: Temporary failure in name
  resolution`) for every domain, including `google.com`.
- TCP connections to public IPs (`8.8.8.8:53`, `1.1.1.1:53`,
  `192.168.2.1:53`) timed out from inside the pods.
- The Service IP `10.96.0.10` (CoreDNS) also timed out.

The node itself could reach the internet and could resolve DNS, so the
issue was between the pod network and the node.

## Diagnosis

Three pieces of evidence:

1. `minikube ssh -- sudo iptables -L FORWARD -n -v` showed
   `Chain FORWARD (policy DROP 14 packets, 735 bytes)`. New connection
   attempts were being dropped at the chain's default policy.
2. The Kubernetes chains (`KUBE-FORWARD`, `KUBE-SERVICES`,
   `KUBE-EXTERNAL-SERVICES`, `DOCKER-FORWARD`) ran first but none of them
   accepted the packets. They fell through to the policy.
3. The K8s chain `KUBE-FORWARD` only accepts packets with mark `0x4000`,
   which is set by `KUBE-MARK-MASQ` in the `nat` table. Pods that were
   masqueraded by a different chain (in our case a stale
   `KIND-MASQ-AGENT`) never received that mark and were dropped.

## Decision

Insert two rules at the top of the FORWARD chain to allow traffic from
and to the pod CIDR:

```sh
sudo iptables -I FORWARD 2 -s 10.244.0.0/16 -j ACCEPT
sudo iptables -I FORWARD 2 -d 10.244.0.0/16 -j ACCEPT
```

Plus, more defensively, a rule for established/related connections at
position 1:

```sh
sudo iptables -I FORWARD 1 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
```

These rules are not persistent across `minikube stop && start`. They need
to be re-applied on each cluster start. (We accept this for the workshop.
A real cluster does not have this problem because its CNI and
`kube-proxy` rules are coherent from the start.)

## Consequences

Good:
- Pods can reach the internet again. DNS works. The app can call
  `guce.yahoo.com` for yfinance.
- The fix is a one-liner that can be turned into a `minikube ssh --`
  command in a Makefile or a `minikube` post-start hook.

Bad / trade-offs:
- The rules bypass the Kubernetes-managed `KUBE-FORWARD` chain. They
  will let through any traffic to the pod CIDR, not just masqueraded
  traffic. Acceptable on a single-node cluster; not what you want on a
  multi-node cluster where NetworkPolicy needs to remain authoritative.
- The root cause (the stale `KIND-MASQ-AGENT` and the missing
  `KUBE-MARK-MASQ` path) is still there. We did not fix it; we routed
  around it.
