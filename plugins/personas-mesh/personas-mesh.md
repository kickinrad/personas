---
title: personas-mesh
type: moc
area: "[[Areas/Claude Ecosystem/Marketplaces/personas/personas|personas]]"
author: wils
created: 2026-04-27
tags:
  - claude-code
  - plugin
  - personas
---

# personas-mesh

> [!abstract] What this is
> State sync for personas across WSL, Windows, and Hetzner via a Tailscale-private git hub

![[README]]

## Plugin guide

- [[Areas/Claude Ecosystem/Marketplaces/personas/plugins/personas-mesh/CLAUDE|CLAUDE]] — plugin-level harness rules (node detection, secrets, sync flow)

## Components

### Skills

- [[Areas/Claude Ecosystem/Marketplaces/personas/plugins/personas-mesh/skills/mesh-doctor/SKILL|mesh-doctor]]
- [[Areas/Claude Ecosystem/Marketplaces/personas/plugins/personas-mesh/skills/setup/SKILL|setup]]
- [[Areas/Claude Ecosystem/Marketplaces/personas/plugins/personas-mesh/skills/status/SKILL|status]]

## Runbooks

- [[Areas/Claude Ecosystem/Marketplaces/personas/plugins/personas-mesh/docs/hetzner-bootstrap|hetzner-bootstrap]] — interactive Hetzner host bootstrap
- [[Areas/Claude Ecosystem/Marketplaces/personas/plugins/personas-mesh/docs/migration-symlink-to-mesh|migration-symlink-to-mesh]] — migrating from local symlink layout to mesh sync
