import base64
import datetime
from decimal import Decimal
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

logger = logging.Logger(None,"INFO")
class ResponseModel(BaseModel):
    content : typing.Union[typing.Mapping,str]
    status_code: int

class MetadataModel(BaseModel):        
    userId:str
    timestamp :typing.Optional[Decimal] = None
    format : str
    size : tuple

class MetadaDataResponseModel(BaseModel):
    userId:str
    timestamp:typing.Optional[Decimal] = None
    format : str
    size : tuple

class MetadataInputModel(BaseModel):
    userId:str
    timestamp:typing.Optional[Decimal] = None

class S3Writer():
    """
    S3Writer class to Put, Get and Delete the Images/objects
    :parameters
    """
    def __init__(self):
        self.bucket_name = "imagebucket2345" #os.environ.get("IMAGE_BUCKET_NAME")
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
            ContentType=f"image/{metadata.format.lower()}",
        )
            logging.info(f"Successfully uploaded the image to the path {self.bucket_name}/{key}")
            return True
        except:
            logging.error(f"Failed to upload the object, Reason {traceback.format_exc(chain=False)}")
            return False
    
    def get_file_path_from_metadata(self,itemInfo:MetadataModel) -> str:
        return "/".join([itemInfo.userId,str(itemInfo.timestamp),f'{str(itemInfo.timestamp)}.{itemInfo.format.lower()}'])
    
    def get_image(self,itemInfo:MetadaDataResponseModel) -> bytes:
        """
        S3Writer Get function to Get the Images/objects
        :parameters
        -   S3 Key : S3 Key of the stored object
        """
        # s3://imagebucket2345/122445/1734786841/1734786841.jpeg
        # s3://imagebucket2345/122445/1734786033/1734786033.jpeg

        key = self.get_file_path_from_metadata(itemInfo=itemInfo)
        logger.info(key)
        try:
            response = self.client.get_object(
                        Bucket=self.bucket_name,
                        Key=key
                    )
            image_stream =  base64.b64encode(response["Body"].read()).decode('utf-8')
            # BytesIO(response["Body"].read())
            return image_stream
        
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
        tableName = "metadatatable" # os.environ.get("METADATA_TABLE_NAME","metadatatale")
        self.table = self.dynamodb.Table(tableName)
    
    def write_metadata(self,metadata:MetadataModel):
        try:
            print(metadata.model_dump())
            self.table.put_item(Item=metadata.model_dump())
        except:
            logging.error(f"Failed to write metadata {traceback.format_exc(chain=False)}")

    def get_meta_item(self,userId:str,timestamp:int):
        try:
            response = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("userId").eq(userId) &
            boto3.dynamodb.conditions.Key("timestamp").eq(timestamp)
        )   
            #TODO: Update the Response
            if response.get("Items") != []:
                item = response.get("Items")[0]
                return  MetadaDataResponseModel(
                    userId=item.get("userId"),
                    timestamp=item.get("timestamp"),
                    format=item.get("format"),
                    size=item.get("size"))
            else:
                return None
            
        except:
            logging.error(f"Failed to list {traceback.format_exc(chain=False)}")
            return None

    def get_meta_items(self,userId:str):
        try:
            response = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('userId').eq(userId)
        )   
            if response.get("Items") != []:
                return  [ MetadaDataResponseModel(
                    userId=item.get("userId"),
                    timestamp=item.get("timestamp"),
                    format=item.get("format"),
                    size=item.get("size")
                ) for item in response.get("Items") ]
            else:
                return None
            
        except:
            logging.error(f"Failed to list {traceback.format_exc(chain=False)}")
            return None      
           
    def delete_meta_item(self,userId:str,timestamp:int):
        try:
            self.table.delete_item(
                Key={
                    "userId": userId, 
                    "timestamp": timestamp  
                }
            )
            
        except:
            logging.error(f"Failed to delete item {traceback.format_exc(chain=False)}")
            return None

class Metadata:
    def __init__(self,userId:str):
        self.userId = userId
        self.writer =  DynamoDbWriter()

    def extract_metadata(self,imagefile) -> MetadataModel:
        self.model = MetadataModel(
            userId=self.userId,
            format=imagefile.format,
            size=imagefile.size,
            timestamp=Decimal(str(datetime.datetime.now().timestamp()))
        )
        return self.model
    
    def write_image(self,imagefile,imagebytes):
        try:
            S3Repo = S3Writer()
            self.model =  self.extract_metadata(imagefile)
            S3Repo.upload_image(metadata=self.model,body=imagebytes)
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
            return {
                "timestamp":str(metadata.timestamp),
                "image" : image }
        except:
            logging.error(f"Failed to get item {traceback.format_exc(chain=False)}")
            return None
        
    def get_items(self) -> dict:
        dy = DynamoDbWriter()
        S3Repo = S3Writer()
        thumbnails = []
        items = dy.get_meta_items(userId=self.userId)
        try:
            if items:
                for item in items:
                    image = S3Repo.get_image(itemInfo=item)
                    image_bytes = base64.b64decode(image)
                    thumb = Image.open(BytesIO(image_bytes))

                    thumb.thumbnail((150, 150))

                    thumb_io = BytesIO()
                    thumb.save(thumb_io, format="JPEG")
                    thumb.seek(0)
                    thumbnail_base64 = base64.b64encode(thumb_io.getvalue()).decode('utf-8')

                    thumbnails.append({
                        "timestamp" : str(item.timestamp),
                        "thumbnail": thumbnail_base64}
                        )
                return {"thumbnails": thumbnails}
            
            else:
                None

        except:
            logging.error(f"Failed to get items {traceback.format_exc(chain=False)}")
            return None

    def delete_item(self,itemInfo:MetadataInputModel):
        try:
            dy = DynamoDbWriter()
            metadata = dy.get_meta_item(userId=itemInfo.userId,timestamp=itemInfo.timestamp)
            S3Repo = S3Writer()
            image = S3Repo.delete_image(itemInfo=metadata)
            dy.delete_meta_item(userId=itemInfo.userId,timestamp=itemInfo.timestamp)
            return True
        except:
            logging.error(f"Failed to delete items {traceback.format_exc(chain=False)}")
            return None
