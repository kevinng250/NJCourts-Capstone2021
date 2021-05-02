###-------------------------------------------------------------------------------------------------
## this is removing the description details and saving the file but to remove the other meta data have to check
#part 1 ::: to remove the description details like author....and annotation , comments...
import sys
from PDFNetPython3 import *
import boto3
import botocore
import os


BUCKET_NAME = 'sanitized-bucket' # replace with your bucket name
#KEY = 'InputTestDocWMetaDataWithoutRestrictionV3_watermarked.pdf' # replace with your object key
#OUTPUTKEY = KEY.split('.')[0] + "_Sanatized.pdf"
s3 = boto3.resource('s3')

#fileName = 'InputTestDocWMetaDataWithoutRestrictionV3.pdf'
#fileName = 'InputTestDocWMetaDataWithoutRestrictionV3_watermarked.pdf'

#def main():
def main(KEY, OUTPUTKEY,inputKey):   
    PDFNet.Initialize()
    doc = PDFDoc( '/tmp/' +KEY)

    #to remeove the file properties 
    doc.GetTrailer().Erase("Info")
    doc.GetRoot().Erase("Metadata")

    # to remove the annotation
    page_num = 1
    itr = doc.GetPageIterator()
    while itr.HasNext():
        print("Page " + str(page_num) + ": ")
        page_num = page_num + 1
        page = itr.Current()
        num_annots = page.GetNumAnnots()
        print('Annotation number --------------', num_annots)
        i = 0
        while i < num_annots:
            annot = page.GetAnnot(i)
            print(annot)
            i = i + 1
            page.AnnotRemove(0)

        itr.Next()

    doc.Save('/tmp/' + OUTPUTKEY, SDFDoc.e_linearized)

    print('Uploading file into S3')
    #s3.Bucket(BUCKET_NAME).upload_file(Filename='/tmp/' + OUTPUTKEY, Key='/tmp/' + OUTPUTKEY)
    s3.Bucket(BUCKET_NAME).upload_file(Filename= '/tmp/' +OUTPUTKEY, Key= inputKey)
    print("Uplaod Scuessfully to S3")
    
    os.remove('/tmp/' +KEY)
    os.remove('/tmp/' + OUTPUTKEY)


if __name__ == '__main__':
    main()


def lambda_handler(event=None, context=None):
    print("Inside Lambda Function")
    
    #adding 4/10/2021
    try:
        print('file Length = ', len(event['files']))
        print('InputKey = ' , event['files'][0]['key'])
        inputKey = event['files'][0]['key']
        KEY = inputKey.split('/')[2]
        OUTPUTKEY = KEY.split('.')[0] + "_Sanatized.pdf"
        print('--------------')
        print('ObjectName = ' ,KEY)
        print('OutPut Key Name = ' ,OUTPUTKEY)
    except:
        raise Exception("Invalid Input ")
    
    
    
    try:
        #second oparameter is the local file name
        #s3.Bucket(BUCKET_NAME).download_file(KEY,'/tmp/' + KEY)
        s3.Bucket(BUCKET_NAME).download_file(inputKey, '/tmp/' + KEY)
        print("Files has been downloaded into local")
        #main()
        print('ObjectName = ' ,KEY)
        print('OutPut Key Name = ' ,OUTPUTKEY)
        main(KEY,OUTPUTKEY,inputKey)
        print("Check the Bucket..")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
            raise Exception("Object Does not Exist")
        else:
            raise Exception("An error occurred") 
    
    event['selectedOptions']['stripMetaData'] = 0
    return {
        "statusCode": 200,
        'files': event['files'],
        'selectedOptions': event['selectedOptions']
        
    }
    
