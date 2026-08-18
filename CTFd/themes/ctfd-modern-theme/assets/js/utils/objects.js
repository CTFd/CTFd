export function mergeObjects(target, source) {
  for (const key of Object.keys(source)) {
    if (source[key] instanceof Object)
      Object.assign(source[key], mergeObjects(target[key], source[key]));
  }
  Object.assign(target || {}, source);
  return target;
}
