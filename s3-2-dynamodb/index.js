// dependencies
const AWS = require('aws-sdk');
const util = require('util');

// get reference to S3 client
const dynamodb = new AWS.DynamoDB();
const keyRegex = /([^/]+)\/([^/]+)\/(.*)/

exports.handler = async (event, context, callback) => {

    // Read options from the event parameter.
    console.log("Reading options from event:\n", util.inspect(event, {depth: 5}));
    const srcBucket = event.Records[0].s3.bucket.name;
    // Object key may have spaces or unicode non-ASCII characters.
    console.log(decodeURIComponent(event.Records[0].s3.object.key))
    const srcKey    = decodeURIComponent(event.Records[0].s3.object.key.replace(/\+/g, " "));

    const match = keyRegex.exec(srcKey);
    if(!match) {
        console.log("Key did not match pattern.Skipping.")
        return;
    }

    console.log(`Indexing ${srcBucket}/${srcKey}`);
    // Infer the image type from the file suffix.


    console.log(match[0]);
    console.log(match[1]);
    console.log(match[2]);
    console.log(match[3]);
    const userId = match[1];
    const epsilonTime = match[2];
    const uniqueUserId = userId + "/" + epsilonTime;
    const file = match[3];
    keyUrl = "https://" + srcBucket + ".s3.amazonaws.com/" + srcKey;
    const indexItem = {};

    indexItem['UniqueUserId'] = {S: uniqueUserId};
    indexItem['epsilonTime'] = {S: epsilonTime};
    indexItem['FileName'] = {S: file};
    indexItem['BucketName'] = {S: srcBucket};
    indexItem['Key'] = {S: keyUrl};

    console.log("Putting index item");
    return putItem(indexItem);

   
};

function putItem(indexItem) {
    var putParams= {
        TableName: "StoredS3DocumentKeys",
        Item: indexItem
    };
    return dynamodb.putItem(putParams).promise();
}
