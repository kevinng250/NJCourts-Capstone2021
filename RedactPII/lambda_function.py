import boto3
import io
import sys
#import psutil
import time
import math
import PIL.Image, PIL.ImageDraw, PIL.ImageFont
import logging
from botocore.exceptions import ClientError
import os
from PDFNetPython3 import *


s3_connection = boto3.client('s3')

def process_text_detection(bucket, documentName):
    
    #Get the document from S3                          
    s3_response  = s3_connection.get_object(
        Bucket=bucket,
        Key=documentName
    )
    #s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=PIL.Image.open(stream)
    s=''
    # Detect text in the document
    client = boto3.client('textract')
    response = client.detect_document_text(
        Document={'S3Object': {'Bucket': bucket, 'Name': documentName}})
        
    #Get the text blocks
    blocks=response['Blocks']
    width, height =image.size
    draw = PIL.ImageDraw.Draw(image)  
    print ('Detected Document Text')
   
    # Create image showing bounding box/polygon the detected lines/text
    for block in blocks:
            if block['BlockType'] == 'WORD':
                s+=block['Text']#print('Detected: ' + block['Text'])
                s+=' '

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    comp_detect = ComprehendDetect(boto3.client('comprehend'))

    print("Detecting languages.")
    languages = comp_detect.detect_languages(s)
    lang_code = languages[0]['LanguageCode']

    print("Detecting personally identifiable information (PII).")
    pii_entities = comp_detect.detect_pii(s, lang_code)
    
    for i in range(len(pii_entities)):
        begin=pii_entities[i]['BeginOffset']
        last=pii_entities[i]['EndOffset']      
        words=s[:begin].split()
        words_between=s[begin:last].split()
        count=0
        for block in blocks:
            if block['BlockType']=='WORD':
                count+=1
            if count>len(words) and count<=(len(words)+len(words_between)): 
                draw=PIL.ImageDraw.Draw(image)
                draw.rectangle([(width * block['Geometry']['Polygon'][1]['X'],
                height * block['Geometry']['Polygon'][0]['Y']),
                (width * block['Geometry']['Polygon'][3]['X'],
                height * block['Geometry']['Polygon'][3]['Y'])],fill='black',
                width=2)
        
    image.save("/tmp/"+documentName)
      
logger = logging.getLogger(__name__)


class ComprehendDetect:
    
    def __init__(self, comprehend_client):
        
        self.comprehend_client = comprehend_client

    def detect_languages(self, text):
        
        try:
            response = self.comprehend_client.detect_dominant_language(Text=text)
            languages = response['Languages']
            logger.info("Detected %s languages.", len(languages))
        except ClientError:
            logger.exception("Couldn't detect languages.")
            raise
        else:
            return languages

    def detect_pii(self, text, language_code):
        
        try:
            response = self.comprehend_client.detect_pii_entities(
                Text=text, LanguageCode=language_code)
            entities = response['Entities']
            logger.info("Detected %s PII entities.", len(entities))
        except ClientError:
            logger.exception("Couldn't detect PII entities.")
            raise
        else:
            return entities
 
def main(inputKey, KEY):
    
    bucket = 'sanitized-bucket'
    document = KEY
    #s3_connection.Bucket(bucket).download_file(document,"tmp/"+document)
    FileName=[]
    s3_connection.download_file(bucket, inputKey, "/tmp/"+document)
    PDFNet.Initialize()
    doc = PDFDoc("/tmp/"+document)
    draw = PDFDraw()

    # The output resolution is set to 92 DPI.
    draw.SetDPI(92)

    page_count=doc.GetPageCount()
    for i in range(page_count):
    # Rasterize the first page in the document and save the result as JPG.
        pg = doc.GetPage(i+1)
        print('Page: '+str(i+1))
        draw.Export(pg, r'/tmp/page'+str(i)+'.jpg', "JPG")
        img_page='page'+ str(i) +'.jpg'
        s3_connection.upload_file( "/tmp/"+img_page, bucket, img_page)
        process_text_detection(bucket,img_page)
        
    for i in range(page_count):
        image1 = PIL.Image.open(r'/tmp/page'+ str(i) +'.jpg')
        im1 = image1.convert('RGB')
        im1.save(r'/tmp/page'+ str(i) +'.pdf')
        FileName.append('/tmp/page'+ str(i) +'.pdf')
    
    #document.close()
    FileName.reverse() 
    PDFNet.Initialize()
    new_doc=PDFDoc()
    new_doc.InitSecurityHandler()
    
    page_num = len(FileName)
    currDoc = 0
    while currDoc < page_num:
        in_doc=PDFDoc(FileName[currDoc]) 
        new_doc.InsertPages(0, in_doc, 1, in_doc.GetPageCount(), PDFDoc.e_none) # inserting at the starting position
        in_doc.Close()
        currDoc = currDoc+1
        
    new_doc.Save("/tmp/"+document, SDFDoc.e_remove_unused)    
    for i in range (page_count):
        os.remove('/tmp/page'+ str(i) +'.pdf')
        os.remove('/tmp/page'+ str(i) +'.jpg')
        s3_connection.delete_object(Bucket=bucket,Key='page'+ str(i) +'.jpg')
    s3_connection.upload_file("/tmp/"+document, bucket, inputKey)
    FileName.clear()

def lambda_handler(event=None, context=None):
    length = len(event['files'])
    
    for i in range(length):
        print("Started working:")
        inputKey = event['files'][i]['key']
        KEY = inputKey.split('/')[2]
        extension=KEY.split('.')[1]
        if extension =="pdf":
            print("doc"+str(i))
            main(inputKey, KEY)
        else:
            continue
    
    return {
    "statusCode": 200,
    "headers": {
        "Content-Type": "application/json"
    },
    "body":"Selected files has been Merged" 
    }