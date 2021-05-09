'use strict';

const AWS = require('aws-sdk');
const stepFunctions = new AWS.StepFunctions();
const { v4: uuidv4 } = require('uuid');

module.exports.init = (event, context, callback) => {
  const body = event.body;
  const files = body.files;
  const selectedOptions = body.selectedOptions;
  const userID = body.userID;
  const submitTime = body.submitTime;
  const srcBucket = body.srcBucket;
  const destBucket = body.destBucket;
  var s3 = new AWS.S3();
  var lambda = new AWS.Lambda();
  var fileKeys = []
  console.log(body)
  if(selectedOptions.elasticSearch === 1 || selectedOptions.sentimentAnalysis ===1 || selectedOptions.redactPII === 1){
    selectedOptions.textract = 1
    for(var i = 0; i < files.length; i++){
      if(files[i].key.includes(".docx") || files[i].key.includes(".vnd.openxmlformats-officedocument.wordprocessingml.document") ){
        selectedOptions.convertDocument = 1
      }
    }
  }
  else{
    selectedOptions.textract = 0
  }
  for(var i = 0; i < files.length; i++){
    fileKeys.push(files[i].key);
  }
  
  const lambdaParams = {
    FunctionName: "VirusScan",
    Payload: JSON.stringify({
        bucketName : "unsanitized-bucket",
        fileKeys : fileKeys
    })
  }


  if(selectedOptions.virusScan === 1){
    console.log("Performing Virus Scan")
    lambda.invoke(lambdaParams).promise()
    .then((data) => {
      console.log(data);
      var payload = JSON.parse(JSON.parse(data.Payload));
      console.log(payload)
      if(payload.hasOwnProperty("Error")){
        console.log("Does this get run?")
        const response = {
          statusCode: '500',
          message: 'Error Found in VirusScan',
          ErrorMessage: JSON.stringify(payload.Error)
        }
        callback(null,response);
      }
      const scannedResults = payload.list
      return scannedResults
    }
    ).then((scannedResults) => {
      var virusFound = false
      var cleanFiles = []
      for( let i = 0; i < files.length; i++) {
        if(scannedResults[i]){
          cleanFiles.push(files[i])
          if(cleanFiles.length == files.length){
            return cleanFiles
          }
        }
        else{
          deleteObjects(files, srcBucket).then()
          const data ={
            "status": "FAILED",
            "cause": "Virus found in " + files[i].displayName
          }
          const response ={
            statusCode: 500,
            data
          }
          callback(null, response)
        }
      }
    }).then((cleanFiles => {
      console.log(cleanFiles)
      return cleanBuckets(cleanFiles, srcBucket, destBucket)
      .then((cleanFiles => {
        deleteObjects(files, srcBucket)
        return cleanFiles
        }
      ))
    })).then((cleanFiles) => {
      console.log(cleanFiles);
      const stepFunctionsParams = {
        stateMachineArn: '<Step-Function ARN',
        name: uuidv4(),
        input: JSON.stringify({
          files: cleanFiles,
          selectedOptions: selectedOptions,
          userID: userID,
          submitTime: submitTime
        })
      }
      startStepFunctions(stepFunctionsParams);
    }).catch((error) => {
      callback(error, null);
    });
    
  }
  else {
    const scannedResults = []
    console.log("Does this get run")
    foo().then(cleanBuckets(files, srcBucket, destBucket)).then(deleteObjects(files, srcBucket))
    .then((cleanFiles) => {
      console.log(cleanFiles);
      const stepFunctionsParams = {
        stateMachineArn: 'Step-Function ARN',
        name: uuidv4(),
        input: JSON.stringify({
          files: files,
          selectedOptions: selectedOptions,
          userID: userID,
          submitTime: submitTime
        })
      }
      startStepFunctions(stepFunctionsParams);
    }).catch((error) => {
      const data ={
        "status": "FAILED",
        "cause": JSON.stringify(error)
      }
      const response ={
        statusCode: 500,
        data
      }
      callback(null, response);
    });
  }



  function cleanBuckets(cleanFiles, srcBucket, destBucket){
    return new Promise((resolve, reject) => {
      console.log("Is this run?")
      for (let i = 0; i < cleanFiles.length; i++) {
        console.log(cleanFiles[i].key)
        var s3params = {
          Bucket: encodeURI('sanitized-bucket'),
          CopySource: encodeURI('/unsanitized-bucket/' + cleanFiles[i].key),
          Key: cleanFiles[i].key
        };
        s3.copyObject(s3params, (err, data) => {
          if(err){
            console.log(err)
            reject(err);
          }
          else{
            console.log("Successfully copied")
            if(i == cleanFiles.length - 1){
              resolve(cleanFiles)
            }
          }
        });
      }
    })
  }

  function deleteObjects(files, srcBucket) {
    return new Promise((resolve, reject) => {
      console.log(srcBucket)
      console.log(files)
      for(let i = 0; i < files.length; i++){
        console.log(files[i].key)
        var s3params = {
          Bucket: encodeURI('unsanitized-bucket'),
          Key: encodeURI(files[i].key)
        }
        s3.deleteObject(s3params, (err, data) =>
        {
          if(err){
            reject(err);
          }
          else{
            console.log("Successfully deleted")
            if( i == files.length - 1){
              resolve()
            }
          }
        })
        // console.log("Successfully deleted")
        // if( i == files.length - 1){
        //   resolve()
        // }
      }
    })
  }

  function startStepFunctions(params) {
    stepFunctions.startSyncExecution(params, (err, data) => {
      if (err) {
        console.log(err);
        const data ={
          "status": "FAILED",
          "cause": JSON.stringify(err)
        }
        const response ={
          statusCode: 500,
          data
        }
        callback(null, response);
      } else {
        console.log(data);
        const response = {
          statusCode: 200,
          data
        };
        callback(null, response);
      }
    });
  }

  function foo(){
    return new Promise((resolve, reject) => {
      resolve()
    })
  }
};

