const AWS = require('aws-sdk');

exports.handler = (event, context, callback) => {

    var lambda = new AWS.Lambda();
    var files = event.files;
    
    var selectedOptions = event.selectedOptions
    selectedOptions.textract = 0
    const elasticSearchParams = {
        FunctionName: "textract2esPython",
        InvocationType: "Event",
        Payload: JSON.stringify({
            bucketName : "sanitized-bucket",
            selectedOptions: selectedOptions,
            files: files
        })
      }
      const sentimentAnalysisParams = {
        FunctionName: "sentiall",
        InvocationType: "Event",
        Payload: JSON.stringify({
            bucketName : "sanitized-bucket",
            selectedOptions: selectedOptions,
            files: files
        })
      }
      const redactionParams = {
        FunctionName: "Redact",
        InvocationType: "Event",
        Payload: JSON.stringify({
            bucketName : "sanitized-bucket",
            selectedOptions: selectedOptions,
            files: files
        })
      }
    if(selectedOptions.elasticSearch === 1){
        
        lambda.invoke(elasticSearchParams, (err, data) => {
            if(err){
                return err
            }
            else{
                console.log(data)
                selectedOptions.elasticSearch = 0
            }
        })
    }
    if(selectedOptions.sentimentAnalysis ===1){
        lambda.invoke(sentimentAnalysisParams, (err, data) => {
            if(err){
                return err
            }
            else{
                console.log(data)
                selectedOptions.sentimentAnalysis = 0
            }
        })
    }
    if(selectedOptions.redactPII ===1)  {
        lambda.invoke(redactionParams, (err, data) => {
            if(err){
                return err
            }
            else{
                console.log(data)
                selectedOptions.redactPII = 0
            }
        })
    }
    selectedOptions.elasticSearch = 0
    selectedOptions.sentimentAnalysis = 0
    selectedOptions.redactPII = 0
    const response = {
        files: files,
        selectedOptions: selectedOptions
    }
    callback(null, response)

    //   lambda.invoke()



};