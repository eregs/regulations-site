import { combineReducers } from 'redux';
import paneReduce from './paneReduce';
import paragraphReduce from './paragraphReduce';

export function activeParagraph(storage) {
  return storage.getState().activeParagraph;
}

export function activePane(storage) {
  return storage.getState().activePane;
}

export default combineReducers({
  activePane: paneReduce,
  activeParagraph: paragraphReduce,
});
