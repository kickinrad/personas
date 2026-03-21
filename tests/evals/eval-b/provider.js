/**
 * Custom promptfoo provider that runs Claude CLI sessions in a persona directory.
 *
 * Handles setup/teardown from test vars, captures stdout, detects file changes,
 * and returns structured output for assertions.
 *
 * Security note: execSync is used intentionally here for controlled test setup/teardown
 * commands defined in YAML config (not user input). This is a test harness, not production code.
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const DEFAULT_TIMEOUT_MS = 300_000; // 5 minutes per test

/**
 * Recursively snapshot a directory — returns a map of relative paths to content hashes.
 */
function snapshotDir(dir) {
  const snapshot = {};
  if (!fs.existsSync(dir)) return snapshot;

  function walk(current, prefix) {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const fullPath = path.join(current, entry.name);
      const relPath = path.join(prefix, entry.name);
      if (entry.isDirectory()) {
        if (entry.name === '.git' || entry.name === 'node_modules') continue;
        snapshot[relPath + '/'] = 'dir';
        walk(fullPath, relPath);
      } else {
        try {
          const content = fs.readFileSync(fullPath);
          snapshot[relPath] = crypto.createHash('sha256').update(content).digest('hex');
        } catch {
          snapshot[relPath] = 'unreadable';
        }
      }
    }
  }

  walk(dir, '');
  return snapshot;
}

/**
 * Diff two snapshots — returns { added, modified, removed }.
 */
function diffSnapshots(before, after) {
  const added = [];
  const modified = [];
  const removed = [];

  for (const [key, hash] of Object.entries(after)) {
    if (!(key in before)) {
      added.push(key);
    } else if (before[key] !== hash) {
      modified.push(key);
    }
  }
  for (const key of Object.keys(before)) {
    if (!(key in after)) {
      removed.push(key);
    }
  }

  return { added, modified, removed };
}

/**
 * Expand ~ to $HOME in a path string.
 */
function expandHome(p) {
  if (p.startsWith('~/') || p === '~') {
    return path.join(process.env.HOME, p.slice(1));
  }
  return p;
}

module.exports = class PersonaProvider {
  constructor(options) {
    this.config = options.config || {};
    this.personaDir = expandHome(this.config.persona_dir || '~/.personas/test-eval-persona');
    this.timeoutMs = this.config.timeout_ms || DEFAULT_TIMEOUT_MS;
    this.model = this.config.model || 'claude-sonnet-4-5-20250929';
  }

  id() {
    return `persona-session:${path.basename(this.personaDir)}`;
  }

  /**
   * Run a shell command synchronously. Returns { stdout, stderr, exitCode }.
   * Used only for controlled setup/teardown commands from test YAML — not user input.
   */
  _exec(cmd, opts = {}) {
    try {
      const stdout = execSync(cmd, {
        cwd: opts.cwd || this.personaDir,
        timeout: opts.timeout || 60_000,
        encoding: 'utf-8',
        env: { ...process.env, ...opts.env },
        stdio: ['pipe', 'pipe', 'pipe'],
      });
      return { stdout: stdout.trim(), stderr: '', exitCode: 0 };
    } catch (err) {
      return {
        stdout: (err.stdout || '').trim(),
        stderr: (err.stderr || '').trim(),
        exitCode: err.status || 1,
      };
    }
  }

  /**
   * Run claude CLI with the given prompt in the persona directory.
   * Returns a promise that resolves to { stdout, stderr, exitCode }.
   */
  _runClaude(prompt) {
    return new Promise((resolve, reject) => {
      const args = [
        '--setting-sources', 'project,local',
        '--model', this.model,
        '-p', prompt,
        '--output-format', 'text',
        '--verbose',
      ];

      const proc = spawn('claude', args, {
        cwd: this.personaDir,
        env: { ...process.env },
        stdio: ['pipe', 'pipe', 'pipe'],
        timeout: this.timeoutMs,
      });

      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', (data) => { stdout += data.toString(); });
      proc.stderr.on('data', (data) => { stderr += data.toString(); });

      const timer = setTimeout(() => {
        proc.kill('SIGTERM');
        reject(new Error(`Claude session timed out after ${this.timeoutMs}ms`));
      }, this.timeoutMs);

      proc.on('close', (code) => {
        clearTimeout(timer);
        resolve({ stdout, stderr, exitCode: code });
      });

      proc.on('error', (err) => {
        clearTimeout(timer);
        reject(err);
      });
    });
  }

  async callApi(prompt, context) {
    const vars = context.vars || {};
    const startTime = Date.now();

    // --- Setup ---
    if (vars.setup) {
      const setupCommands = Array.isArray(vars.setup) ? vars.setup : [vars.setup];
      for (const cmd of setupCommands) {
        const result = this._exec(cmd, { cwd: process.env.HOME });
        if (result.exitCode !== 0) {
          return {
            error: `Setup command failed: ${cmd}\n${result.stderr}`,
          };
        }
      }
    }

    // --- Snapshot before ---
    const snapshotBefore = snapshotDir(this.personaDir);

    // --- Run Claude session ---
    let claudeResult;
    try {
      claudeResult = await this._runClaude(prompt);
    } catch (err) {
      // Still run teardown on error
      if (vars.teardown) {
        const teardownCommands = Array.isArray(vars.teardown) ? vars.teardown : [vars.teardown];
        for (const cmd of teardownCommands) {
          this._exec(cmd, { cwd: process.env.HOME });
        }
      }
      return { error: `Claude session error: ${err.message}` };
    }

    // --- Snapshot after ---
    const snapshotAfter = snapshotDir(this.personaDir);
    const fileChanges = diffSnapshots(snapshotBefore, snapshotAfter);

    // --- Teardown ---
    if (vars.teardown) {
      const teardownCommands = Array.isArray(vars.teardown) ? vars.teardown : [vars.teardown];
      for (const cmd of teardownCommands) {
        this._exec(cmd, { cwd: process.env.HOME });
      }
    }

    const durationMs = Date.now() - startTime;

    return {
      output: claudeResult.stdout,
      metadata: {
        stderr: claudeResult.stderr,
        exitCode: claudeResult.exitCode,
        durationMs,
        fileChanges,
        personaDir: this.personaDir,
      },
    };
  }
};
