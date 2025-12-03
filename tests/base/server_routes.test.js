const request = require('supertest');
const app = require('../../server');

describe('api routes', () => {
  test('mul route', async () => {
    const res = await request(app).get('/api/mul?a=6&b=7');
    expect(res.statusCode).toBe(200);
    expect(res.body.result).toBe(42);
  });

  test('divide route error on zero', async () => {
    const res = await request(app).get('/api/divide?a=1&b=0');
    expect(res.statusCode).toBe(400);
    expect(res.body.error).toMatch(/division by zero/);
  });
});
