import React from 'react';

export default function Definitions(props) {
  return (
    <header className={props.loading ? 'group spinner' : 'group'} >
      <h4>Defined Term</h4>
    </header>
  );
}

Definitions.propTypes = {
  loading: React.PropTypes.bool,
};
