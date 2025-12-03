const request = require('supertest');
const app = require('../../server');

describe('express server', () => {
  test('health endpoint', async () => {
    const res = await request(app).get('/health');
    expect(res.statusCode).toBe(200);
    expect(res.body).toEqual({ status: 'ok' });
  });

  test('api/add works', async () => {
    const res = await request(app).get('/api/add?a=2&b=3');
    expect(res.statusCode).toBe(200);
    expect(res.body.result).toBe(5);
  });
});
