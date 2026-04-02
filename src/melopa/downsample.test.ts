/**
 * Tests for library functions.
 */

import { expect, test } from "vitest";
import { decimate, lttb } from "./downsample";

test("Decimate evenly selects array elements", () => {
  const x = new Float32Array([...Array(16).keys()]);
  const actual = decimate(x, x, 5)[1];
  expect(actual).toStrictEqual(new Float32Array([0, 4, 8, 11, 15]));
});

test("LTTB selects first index for each bin on a straight line", () => {
  const y = new Float32Array([...Array(10)].keys());
  const actual = lttb(y, y, 4)[1];
  expect(actual).toStrictEqual(new Float32Array([0, 1, 5, 9]));
});

test("LTTB selects single peak", () => {
  const x = new Float32Array([...Array(5)].keys());
  const y = new Float32Array([0, 0, 1, 0, 0]);
  const actual = lttb(x, y, 3)[0];
  expect(actual).toStrictEqual(new Float32Array([0, 2, 4]));
});
