// Atea brand colours (https://design.atea.com/cvi/colours) used for chart series
export const ateaPalette = [
  "#008a00", // green
  "#0965b1", // blue
  "#ec7a2e", // orange
  "#097288", // teal
  "#483d7c", // purple
  "#d62429", // red
  "#f6bd18", // yellow
  "#4d575d", // grey
];

export const ateaGreen = ateaPalette[0];
export const ateaRed = ateaPalette[5];

// Always pick the same palette colour for the same text
export function ateaColor(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash * 31 + str.charCodeAt(i)) | 0;
  }
  return ateaPalette[Math.abs(hash) % ateaPalette.length];
}
