export function mergeObjects(target, source) {
  // https://stackoverflow.com/a/65817907
  // Iterate through `source` properties and if an `Object` set property to merge of `target` and `source` properties
  for (const key of Object.keys(source)) {
    if (source[key] instanceof Object)
      Object.assign(source[key], mergeObjects(target[key], source[key]));
  }
  // Join `target` and modified `source`
  Object.assign(target || {}, source);
  return target;
}
