const PARAGRAPH_ACTIVE = 'PARAGRAPH_ACTIVE';
const initialState = '';

export function paragraphActiveEvt(paragraph) {
  return { type: PARAGRAPH_ACTIVE, paragraph };
}

export default function paragraphReduce(state = initialState, action) {
  if (action.type === PARAGRAPH_ACTIVE) {
    return action.paragraph;
  }
  return state;
}
