import React, { useState } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import RingLoader from 'react-spinners/RingLoader';
import PreSignedURL from './PreSignedURL';

const Merge = ({ uploadedFiles, apiResponse }) => {
  const [selectedFilesForMerge, setSelectedFilesForMerge] = useState([]);
  const [preSignedURL, setPreSignedURL] = useState('');
  const [loading, setLoading] = useState(false);

  const checkboxHandle = (e) => {
    const key = e.target.name;
    if (e.target.checked) {
      setSelectedFilesForMerge((prev) => [...prev, key]);
    } else {
      setSelectedFilesForMerge((prev) => prev.filter((each) => each !== key));
    }
  };

  const handleMergeClick = (e) => {
    e.preventDefault();
    setLoading(true);
    const body = {
      files: selectedFilesForMerge,
    };
    // MUST GET THE API ENDPOINT TO WORK
    axios
      .post(
        MERGED_ENDPOINT_HERE,
        body,
      )
      .then((res) => {
        const { data } = res;
        setPreSignedURL(data['Pre-Signed-URL']);
        setLoading(false);
      })
      .catch((error) => {
        /* eslint-disable no-alert */
        if (error.response) {
          const { errorMessage } = error.response.data;
          alert(
            `Error occured while merging selected and the erorr is:\n ${errorMessage}`,
          );
          setSelectedFilesForMerge([]);
          setLoading(false);
        }
        /* eslint-enable no-alert */
      });
  };

  return (
    <div className="container">
      {preSignedURL.length === 0 && !loading && (
        <div className="d-flex flex-column align-items-center justify-content-centers">
          <div>
            <h3>Your Uploaded file(s). You can choose your file for merge or Continue Home</h3>
          </div>
          <div
            className={
              apiResponse.statusCode === 200
                ? 'alert alert-success'
                : 'alert alert-danger'
            }
          >
            {apiResponse.statusCode}
            <span> </span>
            {' '}
            {apiResponse.status}
          </div>
          {apiResponse.cause && (
            <div className="alert alert-danger">
              <p>{apiResponse.cause}</p>
            </div>
          )}
          {uploadedFiles
            && !apiResponse.cause
            && uploadedFiles.map(
              (each, index) => (
                /* eslint-disable react/no-array-index-key */
                <div className="form-check" key={index}>
                  <input
                    className="form-check-input"
                    type="checkbox"
                    value=""
                    name={each.key}
                    id="flexCheckDefault"
                    onChange={checkboxHandle}
                  />
                  <label
                    className="form-check-label"
                    htmlFor="flexCheckDefault"
                  >
                    {each.displayName}
                  </label>
                </div>
              ), /* eslint-enable react/no-array-index-key */
            )}
          <div className="mt-3">
            <a className="btn btn-primary mr-2" href="/">
              Continue Home
            </a>
            {selectedFilesForMerge.length > 1 && (
              <button
                className="btn btn-primary"
                type="submit"
                onClick={handleMergeClick}
              >
                Merge
              </button>
            )}
          </div>
        </div>
      )}
      {preSignedURL.length > 0 && <PreSignedURL preSignedURL={preSignedURL} />}
      <div>
        {loading && <RingLoader loading={loading} color="#9013FE" size={150} />}
      </div>
    </div>
  );
};

Merge.propTypes = {
  apiResponse: PropTypes.objectOf(PropTypes.any).isRequired,
  uploadedFiles: PropTypes.arrayOf(PropTypes.any).isRequired,
};

export default Merge;
