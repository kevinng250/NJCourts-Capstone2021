import boto3
import time
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

def startJob(s3BucketName, objectName):
    response = None
    client = boto3.client('textract', region_name='us-east-1')

    try:
        response = client.start_document_text_detection(
        DocumentLocation={
            'S3Object': {
                'Bucket': s3BucketName,
                'Name': objectName
            }
        })
        return response["JobId"]
    except client.exceptions.InvalidS3ObjectException as err:
        print("run this and then raise exception")
        raise err
        

def isJobComplete(jobId):
    # For production use cases, use SNS based notification 
    # Details at: https://docs.aws.amazon.com/textract/latest/dg/api-async.html
    time.sleep(5)
    client = boto3.client('textract')
    response = client.get_document_text_detection(JobId=jobId)
    status = response["JobStatus"]
    print("Job status: {}".format(status))

    while(status == "IN_PROGRESS"):
        time.sleep(5)
        response = client.get_document_text_detection(JobId=jobId)
        status = response["JobStatus"]
        print("Job status: {}".format(status))

    return status

def getJobResults(jobId):

    pages = []

    client = boto3.client('textract')
    response = client.get_document_text_detection(JobId=jobId)
    
    pages.append(response)
    print("Resultset page recieved: {}".format(len(pages)))
    nextToken = None
    if('NextToken' in response):
        nextToken = response['NextToken']

    while(nextToken):

        response = client.get_document_text_detection(JobId=jobId, NextToken=nextToken)

        pages.append(response)
        print("Resultset page recieved: {}".format(len(pages)))
        nextToken = None
        if('NextToken' in response):
            nextToken = response['NextToken']
    
    return pages

def indexDocument(bucketName, objectName, text, keyUrl, originalName):

    # Update host with endpoint of your Elasticsearch cluster
    #host = "search--xxxxxxxxxxxxxx.us-east-1.es.amazonaws.com
    host = "YOUR-ELASTICSEARCH-DOMAIN"
    region = 'us-east-1'

    if(text):
        service = 'es'
        ss = boto3.Session()
        credentials = ss.get_credentials()
        region = ss.region_name

        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

        es = Elasticsearch(
            hosts = [{'host': host, 'port': 443}],
            http_auth = awsauth,
            use_ssl = True,
            verify_certs = True,
            connection_class = RequestsHttpConnection,
            timeout=30
        )

        document = {
            "name": "{}".format(objectName),
            "bucket" : "{}".format(bucketName),
            "content" : text,
            "keyUrl" : keyUrl,
            "originalName": originalName
        }

        es.index(index="textract", doc_type="document", id=objectName, body=document)

        print("Indexed document: {}".format(objectName))


def error_handler(err):
    if (type(err) is int):
        return False
    else:
        if err[0] == err[1].exceptions.InvalidS3ObjectException:
            raise err[0]


def lambda_handler(event, context):
    # Document

    print(event)
    if "files" not in event:
        return {
            "Status Code": 230,
            "Message": "\'files\' parameter not found in input"
        }
    files = event["files"]
    # if "Bucket" not in event:
    #     return {
    #         "Status Code": 230,
    #         "Message": "\'Bucket\' parameter not found in input"
    #     }
    # s3BucketName = event["Bucket"]
    for file in files:
        if "key" not in file:
            return {
                "Status Code": 230,
                "Message": "\'key\' parameter not found in input[\"files\"]"
            }
        
        documentName = file["key"]
        originalName = ""
        if "displayName" in file:
            originalName = file["displayName"]
        if( ".pdf" not in documentName):
            continue
        s3BucketName = "sanitized-bucket"
        jobId = startJob(s3BucketName, documentName)
        print("Started job with id: {}".format(jobId))
        if(isJobComplete(jobId)):
            response = getJobResults(jobId)
        text = ""
        for resultPage in response:
            for item in resultPage["Blocks"]:
                if item["BlockType"] == "LINE":
                    # print ('\033[94m' +  item["Text"] + '\033[0m')
                    text = text + " " + item["Text"]
        print(text)
        keyUrl = "https://" + s3BucketName + ".s3.amazonaws.com/" + documentName
        indexDocument(s3BucketName, documentName, text, keyUrl, originalName)
        print(documentName + "has been indexed")

    event["selectedOptions"]['elasticSearch'] = 0
    return {
        "statusCode": 200,
        'files': event['files'],
        'selectedOptions': event['selectedOptions']
    }
    
