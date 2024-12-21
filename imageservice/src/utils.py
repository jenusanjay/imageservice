import os
import time
import traceback
import typing
import boto3
import logging
from PIL import Image
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from io import BytesIO

class MetadataModel(BaseModel):        
    userId:str
    timestamp :typing.Optional[int] = int(time.time())
    _format : str
    size : str

class MetadaDataResponseModel(BaseModel):
    userId:str
    timestamp:int
    _format : str
    size : str

class MetadataInputModel(BaseModel):
    userId:str
    timestamp:int

class S3Writer():
    """
    S3Writer class to Put, Get and Delete the Images/objects
    :parameters
    """
    def __init__(self):
        self.bucket_name = os.environ.get("IMAGE_BUCKET_NAME")
        self.client = boto3.client("s3")
    
    def upload_image(self,metadata:MetadataModel,body:bytes):
        """
        S3Writer Upload function to Put the Images/objects
        :parameters
        -   S3 Key : S3 Key of the object to be stored
        -   body : Content of the file to be written
        -   format: File format
        """
        key = self.get_file_path_from_metadata(itemInfo=metadata)
        try:
            self.client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=body,
            ContentType=f"image/{metadata._format.lower()}",
        )
            logging.info(f"Successfully uploaded the image to the path {self.bucket_name}/{key}")
            return True
        except:
            logging.error(f"Failed to upload the object, Reason {traceback.format_exc(chain=False)}")
            return False
    
    def get_file_path_from_metadata(self,itemInfo:MetadataModel) -> str:
        return "/".join(["s3:/",self.bucket_name,itemInfo.userId,itemInfo.timestamp,f'{itemInfo.timestamp}.{itemInfo._format}'])
    
    def get_image(self,itemInfo:MetadaDataResponseModel) -> bytes:
        """
        S3Writer Get function to Get the Images/objects
        :parameters
        -   S3 Key : S3 Key of the stored object
        """
        key = self.get_file_path_from_metadata(itemInfo=itemInfo)
        try:
            response = self.client.get_object(
                        Bucket=self.bucket_name,
                        Key=key
                    )
            return response["Body"].read()
        except:
            logging.error(f"Failed to get the object, Reason {traceback.format_exc(chain=False)}")
            return False        
           
    def delete_image(self,itemInfo:MetadaDataResponseModel) -> bool:
        """
        S3Writer Delete function to Get the Image/object
        :parameters
        -   S3 Key : S3 Key of the stored object that needs to be deleted
        """
        key = self.get_file_path_from_metadata(itemInfo=itemInfo)
        try:
            response = self.client.delete_object(
                        Bucket=self.bucket_name,
                        Key=key
                    )
            return True
        except:
            logging.error(f"Failed to delete the object, Reason {traceback.format_exc(chain=False)}")
            return False     

class DynamoDbWriter():
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")
        tableName = os.environ.get("METADATA_TABLE_NAME")
        self.table = self.dynamodb.Table(tableName)
    
    def write_metadata(self,metadata:MetadataModel):
        try:
            self.table.put_item(Item=metadata.model_dump())
        except:
            logging.error(f"Failed to write metadata {traceback.format_exc(chain=False)}")

    def get_meta_item(self,userId:str,timestamp:int):
        try:
            response = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("partition_key").eq(userId) &
            boto3.dynamodb.conditions.Key("sort_key").eq(timestamp)
        )   
            #TODO: Update the Response
            if response.get("Items") != []:
                return  MetadaDataResponseModel(response.get("Items")[0])
            else:
                return None
            
        except:
            logging.error(f"Failed to list {traceback.format_exc(chain=False)}")
            return None

    def get_meta_items(self,userId:str):
        try:
            response = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("partition_key").eq(userId)
        )   
            if response.get("Items") != []:
                return  [MetadaDataResponseModel(item) for item in response.get("Items") ]
            else:
                return None
            
        except:
            logging.error(f"Failed to list {traceback.format_exc(chain=False)}")
            return None      
           
    def delete_meta_item(self,userId:str,timestamp:int):
        try:
            self.table.delete_item(
                Key={
                    "partition_key": userId, 
                    "sort_key": timestamp  
                }
            )
            
        except:
            logging.error(f"Failed to delete item {traceback.format_exc(chain=False)}")
            return None

class Metadata:
    def __init__(self,userId:str):
        self.userId = userId
        self.writer =  DynamoDbWriter(tableName=os.environ.get("METADATA_TABLE_NAME"))

    def extract_metadata(self,imagefile:Image.ImageFile) -> MetadataModel:
        self.model = MetadataModel(
            userId=self.userId,
            _format=imagefile.format,
            size=imagefile.size
        )
        return self.model
    
    def write_image(self,imagefile:Image.ImageFile):
        try:
            S3Repo = S3Writer()
            self.model =  self.extract_metadata(imagefile)
            S3Repo.upload_image(metadata=self.model)
            self.writer.write_metadata(self.model)
            return self.model
        except:
            logging.error(f"Failed to write image {traceback.format_exc(chain=False)}")
            return None   
    
    def list_all_items(self):
        return  self.writer.list_items(userId=self.userId)
    
    def get_item(self,itemInfo:MetadataInputModel):
        try:
            dy = DynamoDbWriter()
            metadata = dy.get_meta_item(userId=itemInfo.userId,timestamp=itemInfo.timestamp)
            S3Repo = S3Writer()
            image = S3Repo.get_image(itemInfo=metadata)
            return image
        except:
            logging.error(f"Failed to get item {traceback.format_exc(chain=False)}")
            return None
        
    def get_items(self) -> list:
        dy = DynamoDbWriter()
        S3Repo = S3Writer()
        thumbnails = []
        items = dy.get_meta_items(userId=self.userId)
        try:
            for item in items:
                image = S3Repo.get_image(itemInfo=item)
                thumb = Image.open(BytesIO(image))
                image.thumbnail((150, 150))
                thumb_io = BytesIO()
                image.save(thumb_io, format="JPEG")

                thumbnails.append({
                    "timestamp" : item.timestamp,
                    "thumbnail": StreamingResponse(thumb_io, media_type="image/jpeg")}
                    )
                
            return {"thumbnails": thumbnails}
        except:
            logging.error(f"Failed to get items {traceback.format_exc(chain=False)}")
            return None

    def delete_item(self,itemInfo:MetadataInputModel):
        try:
            dy = DynamoDbWriter()
            metadata = dy.get_meta_item(userId=itemInfo.userId,timestamp=itemInfo.timestamp)
            S3Repo = S3Writer()
            image = S3Repo.delete_image(key=metadata)
            dy.delete_meta_item(userId=itemInfo.userId,timestamp=itemInfo.timestamp)
            return image
        except:
            logging.error(f"Failed to delete items {traceback.format_exc(chain=False)}")
            return None