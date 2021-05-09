const AWS = require('aws-sdk');

exports.handler = (event, context, callback) => {
    var lambda = new AWS.Lambda();
    //console.log('Received event:', JSON.stringify(event, null, 2));
    const files = event.files
    const divFiles = filterFileType(files)
    const selectedOptions = event.selectedOptions
    selectedOptions.stripMetaData = 0
    stripMetaData(divFiles.pdfFiles, divFiles.wordFiles)
    .then((response) => {
        response =  {
          files: files,
          selectedOptions: selectedOptions
        }
        callback(null, response)
    })
    
    function filterFileType(files){
        var pdfFiles = []
        var wordFiles = []
        for(var i = 0; i < files.length; i++){
          var filekey = files[i].key;
          if(filekey.includes(".pdf")){
            pdfFiles.push(files[i]);
          }
          else if(filekey.includes(".docx") || filekey.includes(".vnd.openxmlformats-officedocument.wordprocessingml.document") ){
            wordFiles.push(files[i])
          }
        }
        return {
          pdfFiles: pdfFiles,
          wordFiles: wordFiles
        }
      }
    
      function stripMetaData(pdfFiles, wordFiles){
        return Promise.all([stripPDFMetadata(pdfFiles), stripWordMetadata(wordFiles)])
      }
    
      function stripWordMetadata(wordFiles){
        if(wordFiles.length > 0){
          const lambdaParams = {
            FunctionName: "JavaMetaData-test",
            Payload: JSON.stringify({
                bucketName : "sanitized-bucket",
                selectedOptions: selectedOptions,
                files: wordFiles
            })
          }
          return lambda.invoke(lambdaParams).promise();
        }
    
      }
    
      function stripPDFMetadata(pdfFiles){
        console.log(pdfFiles)
        if(pdfFiles.length > 0){
          const lambdaParams = {
            FunctionName: "Sanatized_MetaData_From_PDF",
            Payload: JSON.stringify({
                bucketName : "sanitized-bucket",
                selectedOptions: selectedOptions,
                files: pdfFiles
            })
          }
          return lambda.invoke(lambdaParams).promise()
        }
        
      }
};