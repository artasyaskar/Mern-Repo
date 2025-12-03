const express = require('express');
const path = require('path');
const api = require('./routes/api');
const adv = require('./routes/advanced');

const app = express();
app.use(express.json());

app.use('/api', api);
app.use('/adv', adv);

// Serve static client
app.use(express.static(path.join(__dirname, '..', 'client')));

// Health endpoint
app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

const PORT = process.env.PORT || 3000;
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

module.exports = app;
