         ___        ______     ____ _                 _  ___  
        / \ \      / / ___|   / ___| | ___  _   _  __| |/ _ \ 
       / _ \ \ /\ / /\___ \  | |   | |/ _ \| | | |/ _` | (_) |
      / ___ \ V  V /  ___) | | |___| | (_) | |_| | (_| |\__, |
     /_/   \_\_/\_/  |____/   \____|_|\___/ \__,_|\__,_|  /_/ 
 ----------------------------------------------------------------- 


Hi there! Welcome to AWS Cloud9!

To get started, create some files, play with the terminal,
or visit https://docs.aws.amazon.com/console/cloud9/ for our documentation.


Redact PII

Overview
This lambda function takes PDF and PDF/A format files from JSON input. The code uses two comprehend methods of AWS named Textract and Detect PIIs. The Textract helps in extracting texts from images along with the confidentiality of each word and text. The text generated from textract is then given as input to the Detect PIIs method to find out PIIs present. The detected PIIs are then hidden, using their coordinates, on the input image. The Functionality of this lambda function is divided into 5 parts.
Download the input file from S3 bucket into the local repository. 
Check the extension of the file for .pdf.
The input files are divided into individual pages and these individual pages are then converted to .jpg files.
Once all the files have been successfully converted to .jpg, the textract and redaction is done.
These redacted .jpg files are converted to .pdf files and then merged as one .pdf file. The finally merged file then replaces the original file on S3 bucket.


Packages Used
After trying a series of different packages, PDFNetPython3, is the most efficient and compatible package for achieving the desired target on Linux environment. Outside of the Linux environment, there are few more python packages that can be used. I have also included psutil and logging packages to make sure all the system exceptions are handled properly. The pillow (PIL) package has played a vital role in redacting PIIs using the coordinates. 


Implementation
The code is most compatible with python 3.7 due to package dependencies on AWS lambda platform. The platforms used were VSCode, Cloud9 and AWS Lambda. All the platforms support upto python 3.9 but PDFNetython3 and pillow are compatible with python 3.7 in the Linux environment. The VSCode was set up by providing AWS credentials but Cloud9 and Lambda functions do not require one. The Boto3 and Botocore packages were also required to be imported in VSCode and Cloud9 but these packages are in-built on lambda.


Input
{
  "files": [
    {
      "displayName": "In_Class_Classification.docx",
      "key": "a0aa0f2c-da69-4420-b5ea-bcd06b93ffb1/1617646540564/NDA-Capstone(3).pdf",
      "location": "https://unsanitized-bucket.s3.amazonaws.com//bb41fc75-4e28-4c9b-862e-fe79393aa8a2/1617215163866/bb41fc75-4e28-4c9b-862e-fe79393aa8a216172151638660.vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
  ],
  "selectedOptions": {
    "stripMetaData": 0,
    "textExtract": 0,
    "virusScan": 0,
    "imageRecognition": 0,
    "convertDocument": 0,
    "documentClassification": 0,
    "redactPII": 1
  },
  "userID": "userID",
  "submitTime": "epsilonTime"
}


Output
Page: 1
Detected 1 languages.
Detected 3 PII entities.
Page: 2
Detected 1 languages.
Detected 1 PII entities.

Read Permission: 1
Write Permission: 1


Issues/Errors Occurred while Development
Most of the errors were faced during transitions from VSCode to Cloud9 to AWS Lambda. The issues were majorly related to the compatibility of the platforms with the python version and its inter-dependencies of the packages. Many packages like PyMuPDF, ImageFont from PIL and ImageDraw from PIL were dropped even though these are more effective than the one currently being used. 

The JSON input format that the AWS Lambda takes was also a bit difficult to understand. While the code runs, several files are created, stored in the local space of Lambda and once the final file is uploaded to S3 bucket, the files in the local are deleted. But lambda needs us to specify the local directory by adding “/tmp/” in front of the file names. Rest there were few runtime errors which were rectified by going through the logging information on Cloud Watch.


