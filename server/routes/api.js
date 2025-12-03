const express = require('express');
const { add, mul, safeDivide } = require('../utils/math');

const router = express.Router();

router.get('/add', (req, res) => {
  const a = Number(req.query.a);
  const b = Number(req.query.b);
  res.json({ result: add(a, b) });
});

router.get('/mul', (req, res) => {
  const a = Number(req.query.a);
  const b = Number(req.query.b);
  res.json({ result: mul(a, b) });
});

router.get('/divide', (req, res) => {
  const a = Number(req.query.a);
  const b = Number(req.query.b);
  try {
    res.json({ result: safeDivide(a, b) });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

module.exports = router;
