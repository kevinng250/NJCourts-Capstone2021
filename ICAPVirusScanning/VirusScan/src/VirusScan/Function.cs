using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Amazon;
using Amazon.S3;
using Amazon.S3.Model;
using Amazon.S3.Transfer;
using Amazon.Lambda.Core;
using Newtonsoft.Json;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]
// [assembly: ComVisible(false)]

namespace VirusScan
{
    public class FileEvent {
        public string bucketName {get; set;}
        public String[] fileKeys {get; set;}
    }
    public class S3Error {
        public string Error {get; set;}
    }
    public class Response {
        public List<bool> list {get; set;}
    }
    
    public class Function
    {
        // private const string bucketName = "s3-transfer2-dynamodb";
        // private const string keyName = "NgKevin_STS210_Chapter1.pdf";
        private static readonly RegionEndpoint bucketRegion = RegionEndpoint.USEast1;
        private static IAmazonS3 client;
        /// <summary>
        /// A simple function that takes a string and does a ToUpper
        /// </summary>
        /// <param name="input"></param>
        /// <param name="context"></param>
        /// <returns></returns>
        public String FunctionHandler(FileEvent input, ILambdaContext context)
        {   
            
            // GetObjectRequest request = new GetObjectRequest{
            //     BucketName = bucketName,
            //     Key = keyName
            // }
            foreach(String key in input.fileKeys){
                Console.WriteLine(key);
            }
            string bucketName = input.bucketName;
            List<bool> list = new List<bool>();
            client = new AmazonS3Client(bucketRegion);
            foreach(String keyName in input.fileKeys){
                string filePath = "/tmp/" + keyName;
                TransferUtility fileTransferUtility = new TransferUtility(client);
                try {
                    fileTransferUtility.Download(filePath, bucketName, keyName);
                } catch (AmazonS3Exception ex){
                    S3Error errorMessage = new S3Error(){
                        Error = ex.ToString()
                    };
                    return JsonConvert.SerializeObject(errorMessage);
                }
                // string[] files = Directory.GetFiles("/tmp/");
                // foreach(string item in files){
                //     Console.WriteLine(item);
                // }
                VirusScan.ICAP icap = new VirusScan.ICAP("<AVSCAN-IP>",1344,"SYMCScanResp-AV", 100);
                
                try{
                    Console.WriteLine("File Scanning");
                    bool res = icap.scanFile(filePath);
                    list.Add(res);
                    File.Delete(filePath);
                    Console.WriteLine(res + "\n");
                }
                catch (Exception ex)
                {
                    Console.WriteLine("Could not scan file " + filePath + ex);
                    return "Could not scan file " + filePath + ex;
                }
            }
            Response response = new Response(){
                list = list
            };
            string output = JsonConvert.SerializeObject(response);
            return output;
            
        }



    }
}
