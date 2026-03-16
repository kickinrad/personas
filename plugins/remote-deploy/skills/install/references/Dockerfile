FROM node:22-slim

# Build dependencies for native modules (better-sqlite3 etc.)
RUN apt-get update && apt-get install -y \
    python3 make g++ curl git \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Run as non-root node user (UID 1000)
USER node
WORKDIR /workspace

# Default: headless pipe mode
ENTRYPOINT ["claude", "--print"]
