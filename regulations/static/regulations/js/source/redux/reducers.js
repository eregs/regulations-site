import { combineReducers } from 'redux';
import paragraphReduce from './paragraphReduce';

export function activeParagraph(storage) {
  return storage.getState().activeParagraph;
}

export default combineReducers({
  activeParagraph: paragraphReduce,
});
