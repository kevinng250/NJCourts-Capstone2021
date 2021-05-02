import sys
from PDFNetPython3 import *
import boto3
import botocore
import os


BUCKET_NAME = 'sanitized-bucket' # replace with your bucket name
#KEY = 'Assignment1_Sol.pdf' # replace with your object key
#KEY = 'Assignment1_Sol.docx'
#KEY = 'Assignment1_Sol_PDFA.pdf'
#extension = KEY.split('.')[1]
#OUTPUTKEY = KEY.split('.')[0]
s3 = boto3.resource('s3')


def SimpleDocxConvert(input_filename, output_filename):
    print('Inside DocxConversion Method')
    pdfdoc = PDFDoc()
    
    print('dummy pdfdoc is created')
    print('input_filename = ', input_filename)
    print('output_filename =', output_filename)
    
    print('Calling OfficeConversion')
    Convert.OfficeToPDF(pdfdoc,   input_filename, None)
    print('Conversion done')
    
    # save the result
    pdfdoc.Save('/tmp/' + output_filename, SDFDoc.e_linearized)
    print("Docx converted to PDF, fileName = " + output_filename )


def PrintResults(pdf_a, filename):
    print('Inside PrintResult Method for Compliance Test')
    err_cnt = pdf_a.GetErrorCount()
    if err_cnt == 0:
        print(filename + ": OK.")
    else:
        print(filename + " is NOT a valid PDFA.")
        i = 0
        while i < err_cnt:
            c = pdf_a.GetError(i)
            str1 = " - e_PDFA " + str(c) + ": " + PDFACompliance.GetPDFAErrorMessage(c) + "."
            if True:
                num_refs = pdf_a.GetRefObjCount(c)
                if num_refs > 0:
                    str1 = str1 + "\n   Objects: "
                    j = 0
                    while j < num_refs:
                        str1 = str1 + str(pdf_a.GetRefObj(c, j))
                        if j < num_refs-1:
                            str1 = str1 + ", "
                        j = j + 1
            print(str1)
            i = i + 1
        print('')	



#def main():
def main(KEY, OUTPUTKEY,inputKey,extension, pdfFlag):    
    print('Inside Main Method')
    PDFNet.Initialize()
    print('PDF Intizilse ') 
    
    docFlag = False
    # convert the doc to pdf first
    if extension =='docx':
        print('Calling  docx to pdf convertor Method ')
        SimpleDocxConvert( '/tmp/'+ KEY,  OUTPUTKEY+".pdf")
        docFlag = True
        
    PDFNet.SetColorManagement()     # Enable color m    anagement (required for PDFA validation).
    print('Color is set')
    
    #  convert pdfA 
    #filename = OUTPUTKEY+".pdf"
    filename = '/tmp/' + OUTPUTKEY + ".pdf"
    
    #chnages to save the word to pdf conversion for elastic search, 04/25/21
    if pdfFlag == True:
        pdfFileName = inputKey.split('.')[0] + '.pdf'
        s3.Bucket(BUCKET_NAME).upload_file(Filename=filename, Key=pdfFileName)
        print("Pdf converted file is uplaod to bucket")

    
    print('Convert to a PDFA format')
    pdf_a = PDFACompliance(True, filename, None, PDFACompliance.e_Level2B, 0, 0, 10)
    print('Converted Sucessfully')
    
    #filename = OUTPUTKEY + "_PDFA.pdf"
    filename = '/tmp/' + OUTPUTKEY + "_PDFA.pdf"
    print('Saving the file in local')
    pdf_a.SaveAs( filename, False)
    print(' file Saved')
    pdf_a.Destroy()
    print(" PDFA Saved in local, Now testing the Compliance/ Validating PDFA format")
    
    
    # Re-validate the document after the conversion...
    pdf_a = PDFACompliance(False,  filename, None, PDFACompliance.e_Level2B, 0, 0, 10)
    PrintResults(pdf_a, filename)
    pdf_a.Destroy()
    print("PDFA Compliance test completed.")
    
    #Saving into S3
    print('Uploading file into S3')
    objectName = inputKey.split('.')[0] + '_PDFA.pdf'
    #s3.Bucket(BUCKET_NAME).upload_file(Filename=filename, Key=filename)
    s3.Bucket(BUCKET_NAME).upload_file(Filename=filename, Key=objectName)
    print("Uplaod Scuessfully to S3")
    
    os.remove('/tmp/' +KEY)
    os.remove(filename)
    if docFlag:
        os.remove('/tmp/' +OUTPUTKEY+".pdf")
    print("Files has been remove from local")
    
    

## main block
if __name__ == '__main__':
        try:
            #s3.Bucket(BUCKET_NAME).download_file(KEY, 'Assignment1_Sol.docx') , second oparameter is the local file name
            s3.Bucket(BUCKET_NAME).download_file(KEY,  KEY)
            print("Files has been downloaded into local")
            main()
            print("Check the Bucket..")
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise


def lambda_handler(event=None, context=None):
    print("Inside Lambda Function")
    
    print('file Length = ', len(event['files']))
    length = len(event['files'])
    
    for i in range(length):
        try:
            print('file Array Length = ', len(event['files']))
            print('InputKey = ' , event['files'][i]['key'])
            inputKey = event['files'][i]['key']
            KEY = inputKey.split('/')[2]
            extension = KEY.split('.')[1]
            OUTPUTKEY = KEY.split('.')[0]
        except:
            raise Exception("Invalid Input")
            
        
        pdfFlag = False # chnages to save the pdf version fo the docx file for elastic search or sentimental analysis
        if extension != 'pdf':
            extension = 'docx'
            KEY = OUTPUTKEY + '.docx'
            if ((event['selectedOptions']['elasticSearch'] == 1) or (event['selectedOptions']['sentimentAnalysis'] == 1) or (event['selectedOptions']['redactPII'] == 1) ):
                pdfFlag = True
                event['files'][i]['key'] = inputKey.split('.')[0] + '.pdf'
            
        
        print('--------------')
        print('ObjectName = ' ,KEY)
        print('Extension = ' ,extension)
        print('OutPut Key Name = ' ,OUTPUTKEY)
        
        try:
            #second oparameter is the local file name
            #s3.Bucket(BUCKET_NAME).download_file(KEY,'/tmp/' + KEY)
            s3.Bucket(BUCKET_NAME).download_file(inputKey, '/tmp/' + KEY)
            print("Files has been downloaded into local")
            #main()
            main(KEY,OUTPUTKEY,inputKey,extension, pdfFlag)
            print("Check the Bucket..")
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
                raise Exception("Object Does not Exist")
            else:
                raise Exception("An error occurred") 
    
    
    event['selectedOptions']['convertDocument'] = 0
    return {
        'statusCode': 200,
        'files': event['files'],
        'selectedOptions': event['selectedOptions']
    }
    

