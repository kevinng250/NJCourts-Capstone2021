
import sys
import os
import boto3
import botocore
from PDFNetPython3 import *


BUCKET_NAME = 'doc2pdf-temp'
MergedfileName = '/tmp/' + 'MergeFile.pdf'
InputKeys = ['Gagan_Shrivastava_Resume.pdf', 
            'Homework 1.pdf',
            'Assignment1_Sol.docx']

InputKeys.reverse()

print(InputKeys)

s3 = boto3.resource('s3')
fileNames =[]   
docxTempFiles = []         

def main():
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

    s3.Bucket(BUCKET_NAME).upload_file(Filename=MergedfileName, Key=MergedfileName)
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

    main()



def lambda_handler(event=None, context=None):
    print("Inside Lambda Function")
    ## main block
    for KEY in InputKeys:
        extension = KEY.split('.')[1]
        #if KEY.__contains__('.pdf'):
        if extension == 'pdf':            
            s3.Bucket(BUCKET_NAME).download_file(KEY, '/tmp/' + KEY)
            fileNames.append(KEY)
        #elif KEY.__contains__('.docx'):
        elif extension =='docx':    
            docxTempFiles.append(KEY)
            s3.Bucket(BUCKET_NAME).download_file(KEY, '/tmp/' + KEY)
            SimpleDocxConvert( '/tmp/' + KEY, KEY.split('.')[0]+".pdf")
            fileNames.append(KEY.split('.')[0]+".pdf")
            

    print("Files has been downloaded into local")
    print('File Names are ::::>>>>' , fileNames)

    main()
    print('Check the Bucket....')
    fileNames.clear()
    docxTempFiles.clear()
    
    #event['selectedOptions']['Merging'] = 0
    return {
        "statusCode": 200,
        "body" : event
        
    }
