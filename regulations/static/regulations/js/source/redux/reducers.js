import { combineReducers } from 'redux';
import paneReduce from './paneReduce';
import locationReduce from './locationReduce';

export function activeParagraph(storage) {
  return storage.getState().activeLocation.paragraph;
}

export function activeSection(storage) {
  return storage.getState().activeLocation.section;
}

export function activePane(storage) {
  return storage.getState().activePane;
}

export default combineReducers({
  activePane: paneReduce,
  activeLocation: locationReduce,
});
