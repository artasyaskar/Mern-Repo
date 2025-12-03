const { add, mul, safeDivide } = require('../../server/utils/math');

describe('math utils', () => {
  test('add integers', () => {
    expect(add(2, 3)).toBe(5);
  });
  test('mul integers', () => {
    expect(mul(4, 5)).toBe(20);
  });
  test('divide happy path', () => {
    expect(safeDivide(10, 2)).toBe(5);
  });
  test('divide by zero throws', () => {
    expect(() => safeDivide(1, 0)).toThrow('division by zero');
  });
});
