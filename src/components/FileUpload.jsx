import React, { useState } from 'react';
import PropTypes from 'prop-types';
import S3 from 'react-aws-s3';
import FileUploadForm from './FileUploadForm';
import ProcessSelection from './ProcessSelection';

const selectObecjtSkeleton = {
  stripMetaData: 0,
  elasticSearch: 0,
  virusScan: 0,
  convertDocument: 0,
  sentimentAnalysis: 0,
  redactPII: 0,
};

const FileUpload = ({ userID }) => {
  const [submitTime, setSubmitTime] = useState('');
  const [files, setFiles] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedOptions, setSelectedOptions] = useState(selectObecjtSkeleton);
  const [processSelection, setProcessSelection] = useState(false);
  const [keepOriginalFiles, setKeepOriginalFiles] = useState(false);

  const FileAlreadySelected = (fileToBeCheck) => {
    let response = false;
    files.forEach((file) => {
      if (file.name === fileToBeCheck.name) {
        response = true;
      }
    });
    return response;
  };

  const checkFileSize = (event) => {
    const AllFiles = event.target.files;
    const size = 10000000;
    let err = '';
    const filesList = [];
    if (files.length >= 5) {
      err
        += 'Too many files upload. Please either remove individual file or all files to upload new files.';
    } else {
      for (let x = 0; x < AllFiles.length; x += 1) {
        if (AllFiles[x].size > size) {
          err += `${AllFiles[x].name}is too large, please pick a smaller file\n`;
        } else if (FileAlreadySelected(AllFiles[x])) {
          err += `File ${AllFiles[x].name} already exist.`;
        } else {
          filesList.push(AllFiles[x]);
        }
      }
    }
    if (err !== '') {
      return [false, err];
    }

    return [true, filesList];
  };

  const onChangeHandler = (event) => {
    const [result, value] = checkFileSize(event);
    if (result) {
      setFiles([...files, ...value]);
    } else {
      /* eslint-disable no-alert, no-param-reassign */
      event.target.value = null;
      alert(value);
      /* eslint-enable no-alert, no-param-reassign */
    }
  };

  const resetFormInputs = () => {
    /* eslint-disable no-param-reassign */
    Array.from(document.querySelectorAll('input[type=file]')).forEach(
      (input) => {
        input.value = '';
      },
    );
    /* eslint-enable no-param-reassign */
  };

  const uploadFiles = (prefixTime) => {
    setSubmitTime(prefixTime);
    const config = {
      bucketName: process.env.REACT_APP_BUCKET_NAME,
      dirName: `${userID}/${prefixTime}`,
      region: process.env.REACT_APP_REGION,
      accessKeyId: process.env.REACT_APP_ACCESS_ID,
      secretAccessKey: process.env.REACT_APP_ACCESS_KEY,
      s3Url: HERE_GOES_URL_TO_S3_BUCKET, //NEED TO SET THIS TO S3 URL
    };

    const ReactS3Client = new S3(config);
    files.forEach((each, index) => {
      ReactS3Client.uploadFile(each, userID + prefixTime + index)
        .then((data) => {
          if (data.status === 204) {
            setUploadedFiles((prevState) => [
              ...prevState,
              {
                displayName: each.name,
                key: data.key,
                location: data.location,
              },
            ]);
          }
          if (index === files.length - 1) {
            setTimeout(() => {
              setProcessSelection(!processSelection);
              setFiles([]);
            }, 2000);
          }
        })
        .catch((err) => {
          /* eslint-disable no-alert */
          alert(`File Upload failed with ${err.status} ${err.statusText}`);
          /* eslint-enable no-alert */
        });
    });
  };

  const resetFormANDFiles = () => {
    resetFormInputs();
    setFiles([]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    uploadFiles(Date.now());
    resetFormANDFiles();
  };

  const handleFileRemove = (fileName) => {
    setFiles((prev) => prev.filter((file) => file.name !== fileName));
    if (files.length === 1) {
      resetFormANDFiles();
      setSelectedOptions(selectObecjtSkeleton);
    }
  };

  const handleRemoveAllFiles = () => {
    resetFormANDFiles();
    setSelectedOptions(selectObecjtSkeleton);
  };
  return (
    <>
      {!processSelection ? (
        <FileUploadForm
          onChangeHandler={onChangeHandler}
          handleSubmit={handleSubmit}
          handleFileRemove={handleFileRemove}
          handleRemoveAllFiles={handleRemoveAllFiles}
          setSelectedOptions={setSelectedOptions}
          files={files}
          keepOriginalFiles={keepOriginalFiles}
          setKeepOriginalFiles={setKeepOriginalFiles}
        />
      ) : (
        <ProcessSelection
          selectedOptions={selectedOptions}
          uploadedFiles={uploadedFiles}
          userID={userID}
          submitTime={submitTime}
        />
      )}
    </>
  );
};

FileUpload.propTypes = {
  userID: PropTypes.string.isRequired,
};

export default FileUpload;
