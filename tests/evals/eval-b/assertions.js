/**
 * Shared assertion functions for promptfoo persona evals.
 *
 * promptfoo inline JS assertions run in a sandboxed VM without require().
 * Using file:// references loads this as a proper Node.js module with full access.
 *
 * Each exported function receives (output, context) and returns a GradingResult:
 * { pass: boolean, score: number, reason: string }
 * context.vars contains test variables; context.test contains test metadata.
 */

const fs = require('fs');
const path = require('path');

const PERSONA_DIR = path.join(process.env.HOME, '.personas/test-eval-persona');

// ─── Helpers ───────────────────────────────────────────────────────

/** Wrap a check into a promptfoo GradingResult (requires pass, score, reason) */
function result(pass, reason) {
  return { pass, score: pass ? 1 : 0, reason };
}

function personaPath(...parts) {
  return path.join(PERSONA_DIR, ...parts);
}

function fileExists(relPath) {
  return fs.existsSync(personaPath(relPath));
}

function readFile(relPath) {
  const p = personaPath(relPath);
  if (!fs.existsSync(p)) return null;
  return fs.readFileSync(p, 'utf-8');
}

function readJSON(relPath) {
  const content = readFile(relPath);
  if (!content) return null;
  try { return JSON.parse(content); } catch { return null; }
}

function isExecutable(relPath) {
  try {
    fs.accessSync(personaPath(relPath), fs.constants.X_OK);
    return true;
  } catch { return false; }
}

// ─── Scenario 01: Scaffolding ──────────────────────────────────────

module.exports.dirExists = (output) => {
  const exists = fs.existsSync(PERSONA_DIR);
  return result(exists, exists ? 'Persona directory exists' : 'Persona directory missing');
};

module.exports.claudeMdExists = (output) => {
  const p = personaPath('CLAUDE.md');
  const exists = fs.existsSync(p) && fs.statSync(p).size > 0;
  return result(exists, exists ? 'CLAUDE.md exists and non-empty' : 'CLAUDE.md missing or empty');
};

module.exports.readmeExists = (output) => {
  const exists = fileExists('README.md');
  return result(exists, exists ? 'README.md exists' : 'README.md missing');
};

module.exports.requiredFilesExist = (output) => {
  const checks = [
    'user/profile.md', 'user/memory/MEMORY.md', '.gitignore',
    '.claude/settings.json', '.claude/settings.local.json',
    'hooks.json', 'skills/self-improve/SKILL.md'
  ];
  const missing = checks.filter(f => !fileExists(f));
  return result(missing.length === 0, missing.length === 0 ? 'All required files present' : `Missing: ${missing.join(', ')}`);
};

module.exports.requiredDirsExist = (output) => {
  const dirs = ['user/memory', '.claude/output-styles', 'docs', 'tools'];
  const missing = dirs.filter(d => !fs.existsSync(personaPath(d)));
  return result(missing.length === 0, missing.length === 0 ? 'All required dirs present' : `Missing dirs: ${missing.join(', ')}`);
};

module.exports.guardExecutable = (output) => {
  const p = '.claude/hooks/public-repo-guard.sh';
  if (!fileExists(p)) return result(false, 'public-repo-guard.sh missing');
  const exec = isExecutable(p);
  return result(exec, exec ? 'Guard script is executable' : 'Guard script not executable');
};

module.exports.hooksHas6Types = (output) => {
  const hooks = readJSON('hooks.json');
  if (!hooks || !hooks.hooks) return result(false, 'hooks.json missing or invalid');
  const types = Object.keys(hooks.hooks);
  const required = ['PreToolUse', 'SessionStart', 'Stop', 'StopFailure', 'PreCompact', 'PostCompact'];
  const missing = required.filter(t => !types.includes(t));
  return result(missing.length === 0, missing.length === 0 ? `All 6 hook types present` : `Missing hooks: ${missing.join(', ')}`);
};

module.exports.hooksPreToolUseMatcher = (output) => {
  const hooks = readJSON('hooks.json');
  if (!hooks) return result(false, 'hooks.json missing');
  const pre = hooks.hooks?.PreToolUse;
  if (!pre) return result(false, 'PreToolUse hook missing');
  const hasMatcher = JSON.stringify(pre).includes('Bash');
  const hasGuard = JSON.stringify(pre).includes('public-repo-guard');
  return result(hasMatcher && hasGuard, hasMatcher && hasGuard ? 'PreToolUse has Bash matcher and guard ref' : 'PreToolUse misconfigured');
};

module.exports.sessionStartMentionsProfile = (output) => {
  const hooks = readJSON('hooks.json');
  if (!hooks) return result(false, 'hooks.json missing');
  const ss = hooks.hooks?.SessionStart;
  if (!ss) return result(false, 'SessionStart hook missing');
  const content = JSON.stringify(ss);
  const ok = content.includes('user/profile.md') && content.includes('command');
  return result(ok, ok ? 'SessionStart mentions profile.md and is command type' : 'SessionStart misconfigured');
};

module.exports.sandboxEnabled = (output) => {
  const settings = readJSON('.claude/settings.json');
  if (!settings) return result(false, 'settings.json missing');
  const ok = settings.sandbox?.enabled === true;
  return result(ok, ok ? 'Sandbox enabled' : 'Sandbox not enabled');
};

module.exports.marketplaceConfigured = (output) => {
  const settings = readJSON('.claude/settings.json');
  if (!settings) return result(false, 'settings.json missing');
  const hasMarketplace = !!settings.extraKnownMarketplaces?.personas;
  const hasPlugin = settings.enabledPlugins?.['persona-manager@personas'] === true;
  return result(hasMarketplace && hasPlugin, hasMarketplace && hasPlugin ? 'Marketplace and plugin configured' : `Marketplace: ${hasMarketplace}, Plugin: ${hasPlugin}`);
};

module.exports.autoMemoryConfigured = (output) => {
  const local = readJSON('.claude/settings.local.json');
  if (!local) return result(false, 'settings.local.json missing');
  const ok = local.autoMemoryDirectory === 'user/memory';
  return result(ok, ok ? 'autoMemoryDirectory set to user/memory' : `autoMemoryDirectory: ${local.autoMemoryDirectory}`);
};

module.exports.claudeFlagsCorrect = (output) => {
  const content = readFile('.claude-flags');
  if (!content) return result(false, '.claude-flags missing');
  const hasName = content.includes('--name');
  const hasSources = content.includes('--setting-sources');
  return result(hasName && hasSources, `--name: ${hasName}, --setting-sources: ${hasSources}`);
};

module.exports.gitignoreCorrect = (output) => {
  const content = readFile('.gitignore');
  if (!content) return result(false, '.gitignore missing');
  const hasMcp = content.includes('.mcp.json');
  const hasLocal = content.includes('settings.local.json');
  return result(hasMcp && hasLocal, `.mcp.json: ${hasMcp}, settings.local: ${hasLocal}`);
};

module.exports.gitInitialized = (output) => {
  const exists = fs.existsSync(path.join(PERSONA_DIR, '.git'));
  return result(exists, exists ? 'Git repo initialized' : '.git directory missing');
};

module.exports.domainSkillExists = (output) => {
  // Check for any skill directory besides self-improve
  const skillsDir = personaPath('skills');
  if (!fs.existsSync(skillsDir)) return result(false, 'skills/ directory missing');
  const entries = fs.readdirSync(skillsDir);
  const domainSkills = entries.filter(e => e !== 'self-improve' && fs.statSync(personaPath('skills', e)).isDirectory());
  return result(domainSkills.length > 0, domainSkills.length > 0 ? `Domain skills: ${domainSkills.join(', ')}` : 'No domain skills found');
};

// ─── Scenario 02: SessionStart ─────────────────────────────────────

module.exports.profileModified = (output) => {
  const content = readFile('user/profile.md');
  if (!content) return result(false, 'profile.md does not exist');
  const hasUser = content.includes('Test User');
  return result(hasUser, hasUser ? 'profile.md contains Test User' : 'profile.md does not contain Test User');
};

module.exports.profileNotAllPlaceholders = (output) => {
  const content = readFile('user/profile.md');
  if (!content) return result(false, 'profile.md does not exist');
  const unfilled = (content.match(/\{\{|<PLACEHOLDER>|TODO|FILL_IN/gi) || []).length;
  const lines = content.split('\n').filter(l => l.trim()).length;
  return result(lines > 5 && unfilled < lines / 2, `${lines} content lines, ${unfilled} unfilled placeholders`);
};

// ─── Scenario 03: Memory ───────────────────────────────────────────

module.exports.memoryFilesCreated = (output) => {
  const memDir = personaPath('user/memory');
  if (!fs.existsSync(memDir)) return result(false, 'user/memory/ does not exist');
  const files = fs.readdirSync(memDir).filter(f => f.endsWith('.md') && f !== 'MEMORY.md');
  return result(files.length >= 1, `Found ${files.length} memory files besides MEMORY.md`);
};

module.exports.memoryIndexUpdated = (output) => {
  const content = readFile('user/memory/MEMORY.md');
  if (!content) return result(false, 'MEMORY.md does not exist');
  const hasEntry = content.split('\n').filter(l => l.trim().length > 0).length > 1;
  return result(hasEntry, hasEntry ? 'MEMORY.md has entries beyond header' : 'MEMORY.md is empty/header-only');
};

module.exports.memoryMentionsKeywords = (output) => {
  const memDir = personaPath('user/memory');
  if (!fs.existsSync(memDir)) return result(false, 'memory dir missing');
  const files = fs.readdirSync(memDir).filter(f => f.endsWith('.md'));
  const allContent = files.map(f => fs.readFileSync(path.join(memDir, f), 'utf-8')).join('\n');
  const mentions = /TypeScript|pnpm|trunk.based/i.test(allContent);
  return result(mentions, mentions ? 'Memory mentions keywords' : 'No keyword matches found');
};

module.exports.memoryHasLinks = (output) => {
  const content = readFile('user/memory/MEMORY.md');
  if (!content) return result(false, 'MEMORY.md missing');
  const hasLink = /\[.*?\]\(.*?\.md\)/.test(content);
  return result(hasLink, hasLink ? 'MEMORY.md has links' : 'No links found in MEMORY.md');
};

module.exports.memoryNoSecrets = (output) => {
  const memDir = personaPath('user/memory');
  if (!fs.existsSync(memDir)) return result(true, 'no memory dir to check');
  const files = fs.readdirSync(memDir).filter(f => f.endsWith('.md'));
  const allContent = files.map(f => fs.readFileSync(path.join(memDir, f), 'utf-8')).join('\n');
  const secretPatterns = /(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{30,}|password\s*[:=]\s*\S+|api[_-]?key\s*[:=]\s*\S+)/i;
  const hasSecrets = secretPatterns.test(allContent);
  return result(!hasSecrets, hasSecrets ? 'Memory files contain secret-like patterns' : 'No secrets found');
};

module.exports.memoryConcise = (output) => {
  const memDir = personaPath('user/memory');
  if (!fs.existsSync(memDir)) return result(true, 'no memory dir to check');
  const files = fs.readdirSync(memDir).filter(f => f.endsWith('.md') && f !== 'MEMORY.md');
  const tooLong = files.filter(f => {
    const lines = fs.readFileSync(path.join(memDir, f), 'utf-8').split('\n').length;
    return lines > 50;
  });
  return result(tooLong.length === 0, tooLong.length > 0 ? `Files over 50 lines: ${tooLong.join(', ')}` : 'All memory files concise');
};

// ─── Scenario 05: Public Repo Guard ────────────────────────────────

module.exports.commitBlocked = (output) => {
  const blocked = /block|denied|reject|refuse|cannot commit|guard|prevent/i.test(output);
  return result(blocked, blocked ? 'Commit was blocked' : 'Commit was NOT blocked');
};

module.exports.blockMentionsReason = (output) => {
  const mentionsReason = /user\/|personal data|profile\.md|sensitive/i.test(output);
  return result(mentionsReason, mentionsReason ? 'Block reason mentions user/ or personal data' : 'Block reason not mentioned');
};

module.exports.nonSensitiveCommitSucceeds = (output) => {
  const succeeded = /commit|committed|created|success/i.test(output);
  const blocked = /block|denied|reject|guard/i.test(output);
  return result(succeeded && !blocked, succeeded ? 'Non-sensitive commit succeeded' : 'Commit unexpectedly blocked');
};

// ─── Scenario 06: Sandbox ──────────────────────────────────────────

module.exports.sandboxConfigValid = (output) => {
  const settings = readJSON('.claude/settings.json');
  if (!settings) return result(false, 'settings.json missing');
  const deny = settings.sandbox?.filesystem?.denyRead || [];
  const hasAws = deny.includes('~/.aws');
  const hasSsh = deny.includes('~/.ssh');
  const hasParent = deny.includes('../');
  const ok = hasAws && hasSsh && hasParent;
  return result(ok, `denyRead — ~/.aws: ${hasAws}, ~/.ssh: ${hasSsh}, ../: ${hasParent}`);
};

module.exports.networkRestricted = (output) => {
  const settings = readJSON('.claude/settings.json');
  if (!settings) return result(false, 'settings.json missing');
  const domains = settings.sandbox?.network?.allowedDomains || [];
  return result(domains.length > 0, `${domains.length} allowed domains: ${domains.join(', ')}`);
};

// ─── Scenario 07: Update Migration ─────────────────────────────────

module.exports.allHooksPresent = module.exports.hooksHas6Types;

module.exports.flagsHaveName = (output) => {
  const content = readFile('.claude-flags');
  if (!content) return result(false, '.claude-flags missing');
  const hasName = /--name\s+\S+/.test(content);
  return result(hasName, hasName ? '--name flag present' : '--name flag missing');
};

module.exports.enabledPluginsPresent = (output) => {
  const settings = readJSON('.claude/settings.json');
  if (!settings) return result(false, 'settings.json missing');
  const ok = settings.enabledPlugins?.['persona-manager@personas'] === true;
  return result(ok, ok ? 'persona-manager@personas enabled' : 'enabledPlugins missing or wrong');
};

module.exports.gitignoreHasLocalJson = (output) => {
  const content = readFile('.gitignore');
  if (!content) return result(false, '.gitignore missing');
  const has = content.includes('*.local.json');
  return result(has, has ? '*.local.json pattern present' : '*.local.json pattern missing');
};

module.exports.jsonFilesValid = (output) => {
  const files = ['hooks.json', '.claude/settings.json'];
  const invalid = files.filter(f => readJSON(f) === null);
  return result(invalid.length === 0, invalid.length === 0 ? 'All JSON files valid' : `Invalid: ${invalid.join(', ')}`);
};

module.exports.personaContentPreserved = (output) => {
  const claude = readFile('CLAUDE.md');
  const profile = readFile('user/profile.md');
  const hasIdentity = claude && claude.length > 50;
  const hasProfile = profile && profile.length > 10;
  return result(hasIdentity && hasProfile, `CLAUDE.md: ${hasIdentity ? 'preserved' : 'LOST'}, profile: ${hasProfile ? 'preserved' : 'LOST'}`);
};
