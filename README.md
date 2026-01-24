# Abejar Post-Quantum Cryptography VPN Router

<p align="center">
  <img src="docs/assets/abejar-pqc-logo.svg" alt="Abejar PQC Logo" width="200"/>
</p>

<p align="center">
  <strong>Kyber-1024 Native Implementation</strong>
</p>

<p align="center">
  <a href="https://github.com/vinzabe/abejar-pqc-vpn-kyber-native/actions/workflows/ci.yml"><img src="https://github.com/vinzabe/abejar-pqc-vpn-kyber-native/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/vinzabe/abejar-pqc-vpn-kyber-native/pkgs/container/abejar-pqc-kyber"><img src="https://img.shields.io/badge/Docker-ghcr.io-blue?logo=docker" alt="Docker"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Commercial-red" alt="License"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/PQC-Kyber--1024%20Native-purple?style=for-the-badge" alt="PQC Kyber"/>
  <img src="https://img.shields.io/badge/Security-Quantum--Resistant-green?style=for-the-badge" alt="Quantum Resistant"/>
</p>

<p align="center">
  <a href="#features">Features</a> |
  <a href="#quick-start">Quick Start</a> |
  <a href="#architecture">Architecture</a> |
  <a href="#documentation">Docs</a> |
  <a href="#contact">Contact</a>
</p>

---

## Overview

**Abejar PQC VPN Router (Kyber Native Edition)** is an enterprise-grade VPN routing infrastructure that implements **native Kyber-1024 post-quantum cryptography** directly in the WireGuard protocol. This cutting-edge solution protects your network traffic against both classical and quantum computer attacks.

---

## Post-Quantum Cryptography Security

### The Quantum Threat

Current encryption standards are vulnerable to quantum computers:

| Algorithm | Type | Quantum Vulnerability |
|-----------|------|----------------------|
| RSA-2048 | Asymmetric | Broken by Shor's algorithm |
| ECDH/ECDSA | Asymmetric | Broken by Shor's algorithm |
| AES-256 | Symmetric | Weakened (Grover's) but secure |
| ChaCha20 | Symmetric | Weakened (Grover's) but secure |

### Harvest Now, Decrypt Later

Adversaries are **already collecting encrypted traffic** with the expectation of decrypting it once quantum computers become available. This makes PQC critical for:

- Financial transactions
- Healthcare records
- Government communications
- Long-term business secrets
- Personal privacy

### Our Solution: Kyber-1024

**Kyber** is a NIST-standardized post-quantum key encapsulation mechanism (KEM) that:

- Resists attacks from both classical and quantum computers
- Provides IND-CCA2 security (strongest KEM security level)
- Offers excellent performance (sub-millisecond operations)
- Is based on lattice cryptography (Module-LWE problem)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Hybrid Security Model                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Classical Security          Post-Quantum Security             │
│   ┌─────────────────┐        ┌─────────────────────┐           │
│   │    X25519       │   +    │    Kyber-1024       │           │
│   │  (256-bit EC)   │        │  (NIST Level 5)     │           │
│   └────────┬────────┘        └──────────┬──────────┘           │
│            │                            │                       │
│            └────────────┬───────────────┘                       │
│                         │                                       │
│                         ▼                                       │
│              ┌─────────────────────┐                           │
│              │   Combined Secret    │                           │
│              │   (Defense in Depth) │                           │
│              └─────────────────────┘                           │
│                                                                  │
│   If X25519 is broken → Kyber protects                         │
│   If Kyber is broken  → X25519 protects                        │
│   Both must be broken → Attack succeeds                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Features

### Security
- **Native Kyber-1024 Integration** - Quantum-resistant key exchange at protocol level
- **Hybrid Encryption** - X25519 + Kyber for defense in depth
- **Perfect Forward Secrecy** - Unique session keys for each connection
- **Zero-Trust Architecture** - Localhost-only bindings, no exposed ports

### Performance
- **< 1ms Overhead** - Kyber operations are extremely fast
- **Optimized Routing** - Intelligent traffic management
- **Connection Pooling** - Reduced handshake latency
- **Async I/O** - Non-blocking network operations

### Integration
- **Cloudflare Tunnel Ready** - Secure ingress with PQC TLS
- **Docker Compose** - One-command deployment
- **Any VPN Provider** - Works with any WireGuard-compatible VPN
- **Multi-App Support** - Route multiple applications through single VPN

---

## Quick Start

### Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- WireGuard VPN credentials from your provider
- (Optional) Cloudflare Tunnel token

### Installation

```bash
# Clone the repository
git clone https://github.com/vinzabe/abejar-pqc-vpn-kyber-native.git
cd abejar-pqc-vpn-kyber-native

# Run setup script
./scripts/setup.sh

# Configure environment
nano .env

# Configure WireGuard
nano vpn-router/config/wireguard/wg0.conf

# Start the VPN router
docker compose up -d

# Verify VPN connection
./scripts/vpn-status.sh
```

### Using Pre-built Images

```bash
# Pull the pre-built image
docker pull ghcr.io/vinzabe/abejar-pqc-kyber:latest
```

### Verify Post-Quantum Security

```bash
# Check Kyber handshake
./scripts/test-pqc-handshake.sh

# Verify outgoing IP (should show VPN IP)
docker exec vpn-router curl -s https://ipinfo.io/ip

# Test routing
./scripts/test-connection.sh
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PQC_ENABLED` | `true` | Enable post-quantum cryptography |
| `PQC_ALGORITHM` | `kyber1024` | Kyber security level (512/768/1024) |
| `PQC_HYBRID_MODE` | `true` | Use hybrid X25519 + Kyber mode |
| `PQC_KEY_ROTATION_HOURS` | `24` | Key rotation interval |
| `VPN_INTERFACE` | `wg0` | WireGuard interface name |
| `VPN_NETWORK_CIDR` | `172.25.0.0/16` | Docker network CIDR |
| `VPN_ROUTER_IP` | `172.25.0.2` | VPN router container IP |
| `APP_PORT_START` | `10091` | Starting port for app mappings |
| `APP_PORT_END` | `10100` | Ending port for app mappings |
| `CF_TUNNEL_TOKEN` | - | Cloudflare Tunnel token |
| `CF_TUNNEL_PQC` | `true` | Enable PQC for Cloudflare Tunnel |
| `LOG_LEVEL` | `info` | Logging level (debug/info/warn/error) |
| `LOG_FORMAT` | `json` | Log format (json/text) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        External Network                          │
│  ┌─────────────┐     ┌─────────────────┐     ┌──────────────┐  │
│  │   Users     │     │  Cloudflare CDN │     │ VPN Provider │  │
│  └──────┬──────┘     └────────┬────────┘     └──────┬───────┘  │
│         │                     │                      │          │
└─────────┼─────────────────────┼──────────────────────┼──────────┘
          │ HTTPS               │ PQC TLS              │ Kyber-1024
          │                     │                      │
┌─────────┼─────────────────────┼──────────────────────┼──────────┐
│         ▼                     ▼                      ▲          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Docker Host                           │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │              VPN Router Container                │    │   │
│  │  │  ┌────────────┐  ┌────────────┐  ┌───────────┐  │    │   │
│  │  │  │ WireGuard  │  │  Kyber-1024│  │  Traffic  │  │    │   │
│  │  │  │ Protocol   │──│  Native    │──│  Router   │  │    │   │
│  │  │  └────────────┘  └────────────┘  └───────────┘  │    │   │
│  │  └──────────────────────┬──────────────────────────┘    │   │
│  │                         │                                │   │
│  │  ┌──────────────────────┼──────────────────────────┐    │   │
│  │  │        Cloudflared Container                     │    │   │
│  │  │  ┌─────────────┐     │      ┌────────────────┐  │    │   │
│  │  │  │ PQC TLS 1.3 │─────┴──────│ Tunnel Ingress │  │    │   │
│  │  │  └─────────────┘            └────────────────┘  │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  │                         │                                │   │
│  │  ┌──────────────────────┼──────────────────────────┐    │   │
│  │  │           Application Containers                 │    │   │
│  │  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌───────┐  │    │   │
│  │  │  │Web App │  │  API   │  │Database│  │ Cache │  │    │   │
│  │  │  └────────┘  └────────┘  └────────┘  └───────┘  │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Security Layers

| Layer | Component | Security Feature |
|-------|-----------|------------------|
| 1 | Edge | TLS 1.3 + Kyber (Cloudflare) |
| 2 | Tunnel | Encrypted Cloudflare Tunnel |
| 3 | Container | Localhost-only bindings |
| 4 | Network | Docker network isolation |
| 5 | VPN | WireGuard + Kyber-1024 |
| 6 | Encryption | ChaCha20-Poly1305 |

---

## Documentation

| Document | Description |
|----------|-------------|
| [SECURITY.md](SECURITY.md) | Post-quantum cryptography details and threat model |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture deep dive |
| [docs/INSTALLATION.md](docs/INSTALLATION.md) | Detailed installation guide |
| [docs/CLOUDFLARE_SETUP.md](docs/CLOUDFLARE_SETUP.md) | Cloudflare Tunnel configuration |
| [docs/POST_QUANTUM_CRYPTO.md](docs/POST_QUANTUM_CRYPTO.md) | Technical PQC implementation details |
| [docs/PERFORMANCE.md](docs/PERFORMANCE.md) | Benchmarks and optimization |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues and solutions |

---

## Examples

### SaaS Application

Complete example with FastAPI backend, React frontend, PostgreSQL, and Redis:

```bash
cd examples/saas-application
cp .env.example .env
docker compose up -d
```

See [examples/saas-application/README.md](examples/saas-application/README.md) for details.

---

## License

This software is **commercially licensed**. The core PQC implementation and VPN routing logic are provided as pre-built Docker images.

### What's Included (Free)
- Pre-built Docker images with PQC support
- Configuration templates and examples
- Documentation and support guides

### What Requires License
- Source code for PQC implementation
- Custom modifications
- Enterprise support
- Multi-site deployment

---

## Contact

<p align="center">
  <strong>Abejar Post-Quantum Cryptography Solutions</strong>
</p>

For **full source code access**, **enterprise licensing**, **custom implementations**, and **technical support**:

| | |
|---|---|
| **Email** | grant@abejar.net |
| **Subject** | Abejar PQC VPN - [Your Inquiry] |

### Support Tiers

| Tier | Features |
|------|----------|
| **Community** | Pre-built images, documentation, GitHub issues |
| **Professional** | Source code access, email support, updates |
| **Enterprise** | Custom development, SLA, dedicated support |

---

## Acknowledgments

- [WireGuard](https://www.wireguard.com/) - Modern VPN protocol
- [liboqs](https://openquantumsafe.org/) - Open Quantum Safe library
- [Kyber](https://pq-crystals.org/kyber/) - NIST PQC standard
- [Cloudflare](https://www.cloudflare.com/) - Edge security

---

<p align="center">
  <sub>Built with security in mind by <a href="mailto:grant@abejar.net">Abejar</a></sub>
</p>

<p align="center">
  <sub>Copyright 2024 Abejar. All rights reserved.</sub>
</p>
