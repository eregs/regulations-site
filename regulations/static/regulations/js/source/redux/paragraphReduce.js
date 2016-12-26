const PARAGRAPH_ACTIVE = 'PARAGRAPH_ACTIVE';
const initialState = '';

export function paragraphActive(paragraph) {
  return { type: PARAGRAPH_ACTIVE, paragraph };
}

export default function paragraphReduce(state = initialState, action) {
  if (action.type === PARAGRAPH_ACTIVE) {
    return action.paragraph;
  }
  return state;
}
