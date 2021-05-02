import React from 'react';
import PropTypes from 'prop-types';

const PreSignedURL = ({ preSignedURL }) => (
  <div>
    <h1>Use the URL below to download your merged document.</h1>
    <div><a href={preSignedURL}>Link To Download.</a></div>
  </div>
);

PreSignedURL.propTypes = {
  preSignedURL: PropTypes.string.isRequired,
};

export default PreSignedURL;
