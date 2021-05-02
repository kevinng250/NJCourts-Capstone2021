import React from 'react';
import PropTypes from 'prop-types';

const File = ({ file, handleFileRemove }) => (
  <div>
    <p>
      {file.name}
      <button
        type="button"
        className="close"
        aria-label="Close"
        onClick={() => handleFileRemove(file.name)}
      >
        <span className="p-1" aria-hidden="true">&times;</span>
      </button>
    </p>
  </div>
);

File.propTypes = {
  file: PropTypes.objectOf(PropTypes.any).isRequired,
  handleFileRemove: PropTypes.func.isRequired,
};

export default File;
