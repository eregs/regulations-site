const ACTIVE_LOCATION = 'ACTIVE_LOCATION';
const initialState = { section: '', paragraph: '' };

export function locationActiveEvt(paragraph) {
  const payload = { paragraph };
  const parts = paragraph.split('-');
  payload.section = parts.slice(0, 2).join('-');
  return { type: ACTIVE_LOCATION, payload };
}

export default function locationReduce(state = initialState, action) {
  if (action.type === ACTIVE_LOCATION) {
    return action.payload;
  }
  return state;
}
