// Downsampling algorithms for plotting.

let source = "null";
let xRange = [0, 0];

/** Downsample by selecting every nth point with rounding. */
export function decimate(x, y, size) {
  const step = (y.length - 1) / (size - 1);
  const xOut = new Float32Array(size);
  const yOut = new Float32Array(size);

  for (let index = 0; index < size; index++) {
    const indexIn = Math.round(index * step);
    xOut[index] = x[indexIn];
    yOut[index] = y[indexIn];
  }
  return [xOut, yOut];
}

/**
 * Downsample using the largest triangle three buckets algorithm.
 *
 * Algorithm is described in section 4.2 of
 * https://skemman.is/bitstream/1946/15343/3/SS_MSthesis.pdf and the
 * reference implementation is at
 * https://github.com/sveinn-steinarsson/flot-downsample/blob/master/jquery.flot.downsample.js.
 */
export function lttb(x, y, size) {
  const length = y.length;
  const step = (length - 2) / (size - 2);

  const xOut = new Float32Array(size);
  const yOut = new Float32Array(size);
  xOut[0] = x[0];
  yOut[0] = y[0];
  xOut[size - 1] = x[length - 1];
  yOut[size - 1] = y[length - 1];

  let left = [xOut[0], yOut[0]];
  for (let index = 1; index < size - 1; index++) {
    let areaMax = -1;
    let right = [0, 0];
    let start = Math.floor(step * (index - 1)) + 1;
    let stop = Math.floor(step * index) + 1;

    if (index === size - 2) {
      right = [xOut[size - 1], yOut[size - 1]];
    } else {
      const next = Math.floor(step * (index + 1)) + 1;
      const bsize = next - stop;

      // Calculate right bucket average point.
      for (let bindex = stop; bindex < next; bindex++) {
        right[0] += x[bindex];
        right[1] += y[bindex];
      }
      right = [right[0] / bsize, right[1] / bsize];
    }

    // Find middle bucket point for max triangle area.
    for (let bindex = start; bindex < stop; bindex++) {
      const determinant =
        (left[0] - right[0]) * (y[bindex] - left[1]) -
        (left[0] - x[bindex]) * (right[1] - left[1]);
      const area = 0.5 * Math.abs(determinant);

      if (area > areaMax) {
        areaMax = area;
        xOut[index] = x[bindex];
        yOut[index] = y[bindex];
      }
    }

    // Update left bucket point.
    left = [xOut[index], yOut[index]];
  }

  return [xOut, yOut];
}

export default (args, obj, data, context) => {
  console.log(`Running downsample callback for event ${obj.event_name}.`);
  if (source === "null") {
    source = args.source.data;
  }
  // Skip if array is smaller than downsample limit.
  if (args.size < 3 || args.size >= source.y.length) {
    return;
  }

  let xRangeNew =
    obj.event_name === "rangesupdate"
      ? [obj.x0, obj.x1]
      : [source.x[0], source.x[source.x.length - 1]];
  // Skip if x-range has not changed.
  if (xRange[0] == xRangeNew[0] && xRange[1] == xRangeNew[1]) {
    return;
  }
  xRange = xRangeNew;

  let start = source.x.findIndex((value) => value >= xRange[0]);
  let end =
    start + source.x.slice(start).findIndex((value) => value > xRange[1]);
  console.log(
    `Found indices (${start}, ${end}) for range (${xRange[0]}, ${xRange[1]}).`
  );
  let x = source.x.slice(start, end);
  let y = source.y.slice(start, end);

  if (y.length > args.size) {
    console.log(`Downsampling array length ${y.length} to ${args.size}.`);
    const start = performance.now();
    [x, y] = lttb(x, y, args.size);
    const stop = performance.now();
    console.log(`Downsampled array in ${stop - start}ms.`);
  }

  args.source.data = { x, y };
};
