import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import RingLoader from 'react-spinners/RingLoader';
import Merge from './Merge';

const ProcessSelection = ({
  uploadedFiles,
  selectedOptions,
  userID,
  submitTime,
}) => {
  const [apiResponse, setApiResponse] = useState('');
  const [loading, setLoading] = useState(true);
  // NEED TO SET FOLLOWING VARIABLE WITH RIGHT VALUE
  const APIENDPOINT = API_ENDPOINT_FOR_ACTION;

  useEffect(() => {
    setTimeout(() => {
      const body = {
        body: {
          files: uploadedFiles,
          selectedOptions,
          userID,
          submitTime,
        },
      };
      axios.post(APIENDPOINT, body).then((res) => {
        const { statusCode, data } = res.data;
        const { status } = data;
        if (statusCode === 500) {
          /* eslint-disable no-console */
          const { cause } = data;
          setApiResponse({ statusCode, status, cause });
          /* eslint-enable no-console */
        } else {
          setApiResponse({ statusCode, status });
        }
        setLoading(false);
      }).catch((err) => {
        /* eslint-disable no-console */
        console.log(err);
        setApiResponse({ statusCode: 200, status: 'Most Likely Success', cause: 'Probably API TIMEOUT' });
        setLoading(false);
        /* eslint-enable no-console */
      });
    }, 4000);
  }, []);

  return (
    <>
      {apiResponse && !loading ? (
        <Merge uploadedFiles={uploadedFiles} apiResponse={apiResponse} />
      ) : (
        <RingLoader loading={loading} color="#9013FE" size={150} />
      )}
    </>
  );
};

ProcessSelection.propTypes = {
  uploadedFiles: PropTypes.arrayOf(PropTypes.any).isRequired,
  selectedOptions: PropTypes.objectOf(PropTypes.any).isRequired,
  userID: PropTypes.string.isRequired,
  submitTime: PropTypes.number.isRequired,
};

export default ProcessSelection;
