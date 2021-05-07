import boto3
import io
from io import BytesIO
import sys
import psutil
import time
import math
import PIL.Image, PIL.ImageDraw, PIL.ImageFont
import logging
from botocore.exceptions import ClientError
import fitz
import re
import os
from PDFNetPython3 import *

s3_connection = boto3.resource('s3')
words=[]

def process_text_detection(bucket, documentName):

    
    #Get the document from S3                          
    s3_object = s3_connection.Object(bucket,documentName)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=PIL.Image.open(stream)
    s=''

    # Detect text in the document  
    client = boto3.client('textract')

    #process using S3 object
    response = client.detect_document_text(
        Document={'S3Object': {'Bucket': bucket, 'Name': documentName}})
        
    #Get the text blocks
    blocks=response['Blocks']
    width, height =image.size
    draw = PIL.ImageDraw.Draw(image)  
    print ('Detected Document Text')
   
    # Create image showing bounding box/polygon the detected lines/text
    for block in blocks:
            #print('Type: ' + block['BlockType'])
            if block['BlockType'] == 'WORD':
                s+=block['Text']#print('Detected: ' + block['Text'])
                s+=' '
                #print('Confidence: ' + "{:.2f}".format(block['Confidence']) + "%")

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    comp_detect = ComprehendDetect(boto3.client('comprehend'))

    print("Detecting languages.")
    languages = comp_detect.detect_languages(s)
    #pprint(languages)
    lang_code = languages[0]['LanguageCode']

    print("Detecting personally identifiable information (PII).")
    pii_entities = comp_detect.detect_pii(s, lang_code)
    
    for i in range(len(pii_entities)):
        begin=pii_entities[i]['BeginOffset']#pprint(pii_entities[i]['BeginOffset'])
        last=pii_entities[i]['EndOffset']      
        words_between=s[begin:last].split()
        for x in words_between:
            words.append(x)
            
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
  
class Redactor:
    '''def get_sensitive_data(lines):        
        """ Function to get all the lines """
        EMAIL_REG = r"([\w\.\d]+\@[\w\d]+\.[\w\d]+)"
        for line in lines:   
            # matching the regex to each line
            if re.search(EMAIL_REG, line, re.IGNORECASE):
                search = re.search(EMAIL_REG, line, re.IGNORECASE)
                # yields creates a generator
                # generator is used to return values in between function iterations
                yield search.group(1)'''
  
    # constructor
    def __init__(self, path):
        self.path = path
  
    def redaction(self):
        
        """ main redactor code """ 
        # opening the pdf
        doc = fitz.open(self.path)
          
        # iterating through pages
        for page in doc:
            
            # _wrapContents is needed for fixing alignment issues with rect boxes in some cases where there is alignment issue
            #page._wrapContents()              
            # geting the rect boxes which consists the matching email regex
            #sensitive = self.get_sensitive_data(page.getText("text").split('\n'))
            for data in words:
                areas = page.searchFor(data)
                  
                # drawing outline over sensitive datas
                [page.addRedactAnnot(area, fill = (0, 0, 0)) for area in areas]
                  
            page.apply_redactions()
              
        doc.save('redacted.pdf')
        print("Successfully redacted")
        
        

  
if __name__ == "__main__":
    bucket = 'njcourtstry'
    document = 'NJIT Intern Packet Spring 2021.pdf'
    s3_connection.Bucket(bucket).download_file(document,document)

    PDFNet.Initialize()
    doc = PDFDoc(document)
    draw = PDFDraw()

    # The output resolution is set to 92 DPI.
    draw.SetDPI(92)

    page_count=doc.GetPageCount()
    for i in range(page_count):
    # Rasterize the first page in the document and save the result as JPG.
        pg = doc.GetPage(i+1)
        print('Page: '+str(i+1))
        draw.Export(pg, r'page'+str(i)+'.jpg', "JPG")
        img_page='page'+ str(i) +'.jpg'
        s3_connection.Bucket(bucket).upload_file(img_page,img_page)
        process_text_detection(bucket,img_page)
        
    redactor = Redactor(document)
    redactor.redaction()