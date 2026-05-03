# VTT-Node

**Private Cloud VTT — Zero-Config Self-Hosting for Dungeon Masters**

VTT-Node is a Docker-based appliance that lets any Dungeon Master self-host a professional Virtual Tabletop in under 5 minutes.

## Quick Start

```bash
git clone https://github.com/jahitchcock/Vtt-node.git
cd Vtt-node
./bootstrap.sh
```

## Features

- Zero-config networking via Cloudflare Tunnel
- Dual-engine: Foundry VTT (license required) or MapTool (free)
- Web management dashboard (Phase 3)
- Sigil Rescue migration wizard (Phase 4)
- Nightly encrypted backups + optional S3 sync

## Roadmap

- [x] Phase 1 - Core infrastructure
- [x] Phase 2 - FastAPI management backend
- [ ] Phase 3 - React dashboard
- [ ] Phase 4 - Sigil Rescue migration wizard
- [ ] Phase 5 - Cloudflare Tunnel zero-config polish
- [ ] Phase 6 - Billing & licensing

## License

Open-core Docker stack: AGPL-3.0
Pro dashboard + Sigil Rescue: Proprietary
