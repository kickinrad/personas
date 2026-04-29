---
title: personas-mesh
type: moc
area: "[[personas]]"
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

- [[Resources/Repos/personal/personas/plugins/personas-mesh/CLAUDE|CLAUDE]] — plugin-level harness rules (node detection, secrets, sync flow)

## Components

### Skills

- [[Resources/Repos/personal/personas/plugins/personas-mesh/skills/mesh-doctor/SKILL|mesh-doctor]]
- [[Resources/Repos/personal/personas/plugins/personas-mesh/skills/setup/SKILL|setup]]
- [[Resources/Repos/personal/personas/plugins/personas-mesh/skills/status/SKILL|status]]

## Runbooks

- [[Resources/Repos/personal/personas/plugins/personas-mesh/docs/hetzner-bootstrap|hetzner-bootstrap]] — interactive Hetzner host bootstrap
- [[Resources/Repos/personal/personas/plugins/personas-mesh/docs/migration-symlink-to-mesh|migration-symlink-to-mesh]] — migrating from local symlink layout to mesh sync
