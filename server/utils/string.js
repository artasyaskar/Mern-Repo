function capitalize(s) {
  if (typeof s !== 'string') return '';
  if (!s) return s;
  return s[0].toUpperCase() + s.slice(1);
}

function toCamelCase(s) {
  if (typeof s !== 'string') return '';
  return s
    .replace(/[-_\s]+(.)?/g, (_, c) => (c ? c.toUpperCase() : ''))
    .replace(/^(.)/, (m) => m.toLowerCase());
}

function toKebabCase(s) {
  if (typeof s !== 'string') return '';
  return s
    .replace(/([a-z])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .toLowerCase();
}

function toSnakeCase(s) {
  if (typeof s !== 'string') return '';
  return s
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[\s-]+/g, '_')
    .toLowerCase();
}

function padLeft(s, len, ch = ' ') {
  s = String(s);
  if (s.length >= len) return s;
  return ch.repeat(len - s.length) + s;
}

function padRight(s, len, ch = ' ') {
  s = String(s);
  if (s.length >= len) return s;
  return s + ch.repeat(len - s.length);
}

function truncate(s, len, ellipsis = '...') {
  s = String(s);
  if (s.length <= len) return s;
  return s.slice(0, Math.max(0, len - ellipsis.length)) + ellipsis;
}

function repeat(s, n) {
  return String(s).repeat(Math.max(0, n));
}

function reverse(s) {
  return String(s).split('').reverse().join('');
}

function contains(s, substr) {
  return String(s).indexOf(substr) !== -1;
}

function startsWithAny(s, arr) {
  s = String(s);
  for (const p of arr) {
    if (s.startsWith(p)) return true;
  }
  return false;
}

function endsWithAny(s, arr) {
  s = String(s);
  for (const p of arr) {
    if (s.endsWith(p)) return true;
  }
  return false;
}

function countOccurrences(s, substr) {
  if (!substr) return 0;
  return String(s).split(substr).length - 1;
}

function stripTags(s) {
  return String(s).replace(/<[^>]*>/g, '');
}

function isBlank(s) {
  return String(s).trim().length === 0;
}

function normalizeWhitespace(s) {
  return String(s).replace(/\s+/g, ' ').trim();
}

function safeJsonParse(s, def = null) {
  try {
    return JSON.parse(s);
  } catch (_) {
    return def;
  }
}

function toTitleCase(s) {
  return String(s)
    .toLowerCase()
    .split(/\s+/)
    .map((w) => (w ? w[0].toUpperCase() + w.slice(1) : ''))
    .join(' ');
}

function mask(s, visible = 4, ch = '*') {
  s = String(s);
  if (s.length <= visible) return s;
  const masked = ch.repeat(Math.max(0, s.length - visible));
  return masked + s.slice(-visible);
}

function levenshtein(a, b) {
  a = String(a);
  b = String(b);
  const m = a.length;
  const n = b.length;
  const dp = Array.from({ length: m + 1 }, () => Array(n + 1).fill(0));
  for (let i = 0; i <= m; i++) dp[i][0] = i;
  for (let j = 0; j <= n; j++) dp[0][j] = j;
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      dp[i][j] = Math.min(
        dp[i - 1][j] + 1,
        dp[i][j - 1] + 1,
        dp[i - 1][j - 1] + cost
      );
    }
  }
  return dp[m][n];
}

function wrap(s, width) {
  s = String(s);
  const out = [];
  let line = '';
  for (const ch of s.split(' ')) {
    if ((line + ch).length + (line ? 1 : 0) > width) {
      if (line) out.push(line);
      line = ch;
    } else {
      line = line ? line + ' ' + ch : ch;
    }
  }
  if (line) out.push(line);
  return out.join('\n');
}

function chunk(s, size) {
  s = String(s);
  const res = [];
  for (let i = 0; i < s.length; i += size) res.push(s.slice(i, i + size));
  return res;
}

function between(s, start, end) {
  s = String(s);
  const i = s.indexOf(start);
  if (i === -1) return '';
  const j = s.indexOf(end, i + start.length);
  if (j === -1) return '';
  return s.slice(i + start.length, j);
}

function ensurePrefix(s, prefix) {
  s = String(s);
  return s.startsWith(prefix) ? s : prefix + s;
}

function ensureSuffix(s, suffix) {
  s = String(s);
  return s.endsWith(suffix) ? s : s + suffix;
}

function replaceAll(s, find, rep) {
  return String(s).split(find).join(rep);
}

function removeNonAscii(s) {
  return String(s).replace(/[\x00-\x1F\x7F-\x9F]/g, '');
}

function slugify(s) {
  return String(s)
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-');
}

module.exports = {
  capitalize,
  toCamelCase,
  toKebabCase,
  toSnakeCase,
  padLeft,
  padRight,
  truncate,
  repeat,
  reverse,
  contains,
  startsWithAny,
  endsWithAny,
  countOccurrences,
  stripTags,
  isBlank,
  normalizeWhitespace,
  safeJsonParse,
  toTitleCase,
  mask,
  levenshtein,
  wrap,
  chunk,
  between,
  ensurePrefix,
  ensureSuffix,
  replaceAll,
  removeNonAscii,
  slugify
};
