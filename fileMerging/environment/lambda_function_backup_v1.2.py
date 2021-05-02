
import sys
import os
import boto3
import botocore
from PDFNetPython3 import *


BUCKET_NAME = 'sanitized-bucket'
MergedfileName = '/tmp/' + 'MergeFile.pdf'
#InputKeys = ['Gagan_Shrivastava_Resume.pdf',  'Homework 1.pdf','Assignment1_Sol.docx']

#InputKeys.reverse()

#print(InputKeys)
InputKeys = []
s3 = boto3.resource('s3')
fileNames =[]   
docxTempFiles = []         

def main(path):
    print('Inside Main Method')
    PDFNet.Initialize()

    # Sample  - Merge several PDF documents into one    
    print("_______________________________________________")
    
    new_doc=PDFDoc()
    new_doc.InitSecurityHandler()
    
    page_num = len(fileNames)
    currDoc = 0
    while currDoc < page_num:
        print('File Picked = ' , fileNames[currDoc])
        in_doc=PDFDoc('/tmp/' + fileNames[currDoc]) # file name dena hai
        new_doc.InsertPages(0, in_doc, 1, in_doc.GetPageCount(), PDFDoc.e_none) # inserting at the starting position
        in_doc.Close()
        currDoc = currDoc+1
        
    new_doc.Save(MergedfileName, SDFDoc.e_remove_unused)
    
    print("Done. Result saved in Merge.pdf")

    #s3.Bucket(BUCKET_NAME).upload_file(Filename=MergedfileName, Key=path + '/MergedFile.pdf')
    # uplading the files in new bucket
    s3.Bucket('mergefiles').upload_file(Filename=MergedfileName, Key=path + '/MergedFile.pdf')
    
    print("Uplaod Scuessfully to S3")
	
    # Close the open document to free up document memory sooner than waiting for the
    # garbage collector   
    in_doc.Close()
    new_doc.Close()

    
    #remove the files from local
    os.remove(MergedfileName)
    for key in fileNames:
        os.remove('/tmp/' +key)
    for key in docxTempFiles:
        os.remove('/tmp/' +key)
    
    print('files has been removed from local')
    

#convert the doc file to pdf and save in local
def SimpleDocxConvert(input_filename, output_filename):
    print('Inside Docx conversion Method')
    pdfdoc = PDFDoc()
    # perform the conversion with no optional parameters
    Convert.OfficeToPDF(pdfdoc,input_filename, None)
    # save the result
    pdfdoc.Save('/tmp/' + output_filename, SDFDoc.e_linearized)
    print("Docx converted to PDF, fileName = " + output_filename )



def create_presigned_url(bucket_name, object_name, expiration=3600):
    #Generate a presigned URL to share an S3 object
    
    print("Creating Pre Signed URL")
    print("ObjectName is = " , object_name)
    print("Bucket Name = " , bucket_name)
    print("Url Will exprire in = " , expiration)
    
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


# Main    
if __name__ == '__main__':
    
    for KEY in InputKeys:
        extension = KEY.split('.')[1]
        #if KEY.__contains__('.pdf'):
        if extension == 'pdf':            
            s3.Bucket(BUCKET_NAME).download_file(KEY, KEY)
            fileNames.append(KEY)
        #elif KEY.__contains__('.docx'):
        elif extension =='docx':    
            docxTempFiles.append(KEY)
            s3.Bucket(BUCKET_NAME).download_file(KEY, KEY)
            SimpleDocxConvert(KEY, KEY.split('.')[0]+".pdf")
            fileNames.append(KEY.split('.')[0]+".pdf")
            

    print("Files has been downloaded into local")
    print('File Names are ::::>>>>' , fileNames)

    #main()



def lambda_handler(event=None, context=None):
    print("Inside Lambda Function")
    
    path = event['files'][0]['key']
    path = path.split('/')[0] + '/' + path.split('/')[1]
    print(path)
    
    print('file Length = ', len(event['files']))
    length = len(event['files'])
    for i in range(length):
        print('InputKey = ' , event['files'][i]['key'])
        InputKeys.append(event['files'][i]['key'])
    
    InputKeys.reverse()

    print(InputKeys)
 
    
    ## main block
    for value in InputKeys:
        KEY = value.split('/')[2]
        extension = KEY.split('.')[1]
        #if KEY.__contains__('.pdf'):
        if extension == 'pdf':            
            s3.Bucket(BUCKET_NAME).download_file(value, '/tmp/' + KEY)
            fileNames.append(KEY)
        #elif KEY.__contains__('.docx'):
        #elif extension =='docx':
        else:
            KEY = KEY.split('.')[0] + '.docx'
            docxTempFiles.append(KEY)
            s3.Bucket(BUCKET_NAME).download_file(value, '/tmp/' + KEY)
            SimpleDocxConvert( '/tmp/' + KEY, KEY.split('.')[0]+".pdf")
            fileNames.append(KEY.split('.')[0]+".pdf")
            

    print("Files has been downloaded into local")
    print('File Names are ::::>>>>' , fileNames)

    main(path)
    print('Check the Bucket....')
    
    #changes for the presigned url and for merged file bucket//4/14/2021
    # giving the bucket name = mergefiles
    url = create_presigned_url('mergefiles', path + '/MergedFile.pdf')
    print("PreSignedURl is =" , url)

    fileNames.clear()
    docxTempFiles.clear()
    InputKeys.clear()
    
    #event['selectedOptions']['Merging'] = 0
    return {
        "statusCode": 200,
        "Pre-Signed-URL" : url
        #"body" : event
        
    }
