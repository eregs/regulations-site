let globalStorage = null;

export function setStorage(newStorage) {
  globalStorage = newStorage;
}

export default function storage() {
  if (globalStorage) {
    return globalStorage;
  }
  throw new Error('Redux storage is not set yet');
}
