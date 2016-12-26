const PARAGRAPH_ACTIVE = 'PARAGRAPH_ACTIVE';
const initialState = { section: '', paragraph: '' };

export function paragraphActiveEvt(paragraph) {
  const payload = { paragraph };
  const parts = paragraph.split('-');
  payload.section = parts.slice(0, 2).join('-');
  return { type: PARAGRAPH_ACTIVE, payload };
}

export default function paragraphReduce(state = initialState, action) {
  if (action.type === PARAGRAPH_ACTIVE) {
    return action.payload;
  }
  return state;
}
