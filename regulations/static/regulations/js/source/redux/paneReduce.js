const PANE_ACTIVE = 'PANE_ACTIVE';
const initialState = 'table-of-contents';

export function paneActiveEvt(pane) {
  return { type: PANE_ACTIVE, pane };
}

export default function paneReduce(state = initialState, action) {
  if (action.type === PANE_ACTIVE) {
    return action.pane;
  }
  return state;
}
