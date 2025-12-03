function uniq(arr) {
  return Array.from(new Set(arr));
}

function flatten(arr) {
  return arr.reduce((a, b) => a.concat(b), []);
}

function chunk(arr, size) {
  const out = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
}

function groupBy(arr, fn) {
  return arr.reduce((m, x) => {
    const k = fn(x);
    (m[k] || (m[k] = [])).push(x);
    return m;
  }, {});
}

function partition(arr, fn) {
  const t = [];
  const f = [];
  for (const x of arr) {
    (fn(x) ? t : f).push(x);
  }
  return [t, f];
}

function zip(a, b) {
  const n = Math.min(a.length, b.length);
  const out = [];
  for (let i = 0; i < n; i++) out.push([a[i], b[i]]);
  return out;
}

function unzip(pairs) {
  const a = [];
  const b = [];
  for (const [x, y] of pairs) {
    a.push(x);
    b.push(y);
  }
  return [a, b];
}

function range(n, start = 0) {
  const out = [];
  for (let i = 0; i < n; i++) out.push(start + i);
  return out;
}

function intersect(a, b) {
  const s = new Set(b);
  return a.filter((x) => s.has(x));
}

function difference(a, b) {
  const s = new Set(b);
  return a.filter((x) => !s.has(x));
}

function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function sum(arr) {
  return arr.reduce((a, b) => a + b, 0);
}

function average(arr) {
  return arr.length ? sum(arr) / arr.length : 0;
}

function median(arr) {
  if (!arr.length) return 0;
  const a = arr.slice().sort((x, y) => x - y);
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}

function mode(arr) {
  const m = new Map();
  let best = null;
  let cnt = 0;
  for (const x of arr) {
    const c = (m.get(x) || 0) + 1;
    m.set(x, c);
    if (c > cnt) {
      cnt = c;
      best = x;
    }
  }
  return best;
}

function rotate(arr, k) {
  const n = arr.length;
  if (!n) return arr.slice();
  k = ((k % n) + n) % n;
  return arr.slice(n - k).concat(arr.slice(0, n - k));
}

function take(arr, n) {
  return arr.slice(0, n);
}

function drop(arr, n) {
  return arr.slice(n);
}

function compact(arr) {
  return arr.filter(Boolean);
}

function mapObj(arr, fn) {
  const o = {};
  for (const x of arr) {
    const [k, v] = fn(x);
    o[k] = v;
  }
  return o;
}

function keyBy(arr, fn) {
  const o = {};
  for (const x of arr) {
    o[fn(x)] = x;
  }
  return o;
}

function permutations(arr) {
  const res = [];
  function bt(a, l) {
    if (l === a.length) {
      res.push(a.slice());
      return;
    }
    for (let i = l; i < a.length; i++) {
      [a[l], a[i]] = [a[i], a[l]];
      bt(a, l + 1);
      [a[l], a[i]] = [a[i], a[l]];
    }
  }
  bt(arr.slice(), 0);
  return res;
}

function combinations(arr, k) {
  const res = [];
  function rec(start, path) {
    if (path.length === k) {
      res.push(path.slice());
      return;
    }
    for (let i = start; i < arr.length; i++) {
      path.push(arr[i]);
      rec(i + 1, path);
      path.pop();
    }
  }
  rec(0, []);
  return res;
}

function slidingWindow(arr, size, step = 1) {
  const out = [];
  for (let i = 0; i + size <= arr.length; i += step) out.push(arr.slice(i, i + size));
  return out;
}

function binarySearch(arr, x, cmp = (a, b) => a - b) {
  let lo = 0,
    hi = arr.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    const c = cmp(arr[mid], x);
    if (c === 0) return mid;
    if (c < 0) lo = mid + 1;
    else hi = mid - 1;
  }
  return -1;
}

module.exports = {
  uniq,
  flatten,
  chunk,
  groupBy,
  partition,
  zip,
  unzip,
  range,
  intersect,
  difference,
  shuffle,
  sum,
  average,
  median,
  mode,
  rotate,
  take,
  drop,
  compact,
  mapObj,
  keyBy,
  permutations,
  combinations,
  slidingWindow,
  binarySearch
};
