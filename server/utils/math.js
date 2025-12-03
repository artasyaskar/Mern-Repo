function add(a, b) {
  return Number(a) + Number(b);
}

function mul(a, b) {
  return Number(a) * Number(b);
}

function safeDivide(a, b) {
  if (b === 0) throw new Error('division by zero');
  return Number(a) / Number(b);
}

module.exports = { add, mul, safeDivide };
