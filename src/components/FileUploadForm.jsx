import React from 'react';
import PropTypes from 'prop-types';
import File from './File';

const FileUploadForm = ({
  onChangeHandler,
  handleSubmit,
  handleFileRemove,
  handleRemoveAllFiles,
  setSelectedOptions,
  files,
  keepOriginalFiles,
  setKeepOriginalFiles,
}) => {
  const options = [
    { name: 'stripMetaData', displayName: 'Strip Meta Data', status: 'false' },
    { name: 'elasticSearch', displayName: 'Text-Extract to Elastic Search', status: 'false' },
    { name: 'virusScan', displayName: 'Virus Scan', status: 'false' },
    {
      name: 'convertDocument',
      displayName: 'Convert Document to PDF/A',
      status: 'false',
    },
    {
      name: 'sentimentAnalysis',
      displayName: 'Sentiment Analysis',
      status: 'false',
    },
    { name: 'redactPII', displayName: 'Redact PII', status: 'false' },
  ];

  const checkboxHandle = (e) => {
    if (e.target.checked) {
      const keyName = e.target.name;
      const tmp = {};
      tmp[keyName] = 1;
      setSelectedOptions((prevState) => ({ ...prevState, ...tmp }));
    } else {
      const keyName = e.target.name;
      const tmp = {};
      tmp[keyName] = 0;
      setSelectedOptions((prevState) => ({ ...prevState, ...tmp }));
    }
  };

  const handleSwitchButton = () => {
    setKeepOriginalFiles(!keepOriginalFiles);
  };

  return (
    <div className="container m-2">
      <div>
        <p className="text-justify">
          If uploading more than one file, user can upload multiple files by
          selecting them at once while holding down ctrl or command key or
          uploading each file seperately. By selecting again will append the
          newly selected file to the current list .
          {' '}
          <strong>Maximum 5 files and each file less than 10MB in size.</strong>
        </p>
        <form onSubmit={handleSubmit}>
          <div>
            <div className="form-group">
              <input
                type="file"
                className="form-control-file"
                placeholder="Upload File(s)"
                multiple
                onChange={onChangeHandler}
                accept="application/pdf,.doc,.docx"
              />
            </div>
            <div className="custom-control custom-switch w-100 d-flex">
              <input
                type="checkbox"
                className="custom-control-input"
                id="customSwitches"
                readOnly
                onClick={handleSwitchButton}
                disabled
              />
              <label className="custom-control-label" htmlFor="customSwitches">
                Keep Original File(s)
              </label>
            </div>
            {files.length > 0
              && options.map(
                (each, index) => (
                  /* eslint-disable react/no-array-index-key */
                  <div className="form-check d-flex" key={index}>
                    {each.status === 'true' ? (
                      <input
                        className="form-check-input"
                        type="checkbox"
                        name={each.name}
                        id="flexCheckDefault"
                        onChange={checkboxHandle}
                        disabled
                      />
                    ) : (
                      <input
                        className="form-check-input"
                        type="checkbox"
                        name={each.name}
                        id="flexCheckDefault"
                        onChange={checkboxHandle}
                      />
                    )}
                    <label
                      className="form-check-label"
                      htmlFor="flexCheckDefault"
                    >
                      {each.displayName}
                    </label>
                  </div>
                ), /* eslint-enable react/no-array-index-key */
              )}
            {' '}
            <input
              type="submit"
              value="upload"
              disabled={files.length === 0}
              className="btn btn-primary btn-lg btn-block"
            />
          </div>
        </form>
      </div>
      <div className="mt-5 d-flex flex-column align-items-center">
        {files.length > 0 && (
          <button
            type="button"
            className="btn btn-danger w-25 align-self-center mb-4"
            onClick={handleRemoveAllFiles}
          >
            Clear All
          </button>
        )}
        <div className="d-flex flex-column">
          {files
            && files.map(
              (file, index) => (
                /* eslint-disable react/no-array-index-key */
                <File
                  file={file}
                  key={index}
                  handleFileRemove={handleFileRemove}
                />
              ), /* eslint-enable react/no-array-index-key */
            )}
        </div>
      </div>
    </div>
  );
};

FileUploadForm.propTypes = {
  onChangeHandler: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  handleFileRemove: PropTypes.func.isRequired,
  handleRemoveAllFiles: PropTypes.func.isRequired,
  setSelectedOptions: PropTypes.func.isRequired,
  files: PropTypes.arrayOf(PropTypes.any).isRequired,
  keepOriginalFiles: PropTypes.bool.isRequired,
  setKeepOriginalFiles: PropTypes.func.isRequired,
};

export default FileUploadForm;
