import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from io import BytesIO
from PIL import Image
from src.api import app

client = TestClient(app)

# Helper function to create a mock image
def create_mock_image():
    img = Image.new("RGB", (500, 500), color="blue")  # Create a 500x500 blue image
    img_io = BytesIO()
    img.save(img_io, format="JPEG")
    img_io.seek(0)
    return img_io.getvalue()

@pytest.fixture
def mock_s3():
    with patch("boto3.client") as mock_boto_client:
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client
        yield mock_s3_client

def test_generate_thumbnails(mock_s3):
    mock_image_bytes = create_mock_image()
    mock_s3.get_object.return_value = {"Body": BytesIO(mock_image_bytes)}

    # Step 2: Call the endpoint
    response = client.get("/generate-thumbnails/test-image.jpg")

    # Step 3: Validate response
    assert response.status_code == 200
    data = response.json()
    
    # Check if the number of thumbnails matches the expected sizes
    assert len(data["thumbnails"]) == len(THUMBNAIL_SIZES)

    # Validate each thumbnail
    for thumb, size in zip(data["thumbnails"], THUMBNAIL_SIZES):
        assert thumb["size"] == f"{size[0]}x{size[1]}"
        assert "url" in thumb  # Ensure each thumbnail has a URL

def test_generate_thumbnails_invalid_key(mock_s3):
    # Step 1: Mock the S3 get_object method to raise an error
    mock_s3.get_object.side_effect = Exception("No such key")

    # Step 2: Call the endpoint with an invalid key
    response = client.get("/generate-thumbnails/invalid-image.jpg")

    # Step 3: Validate response
    assert response.status_code == 500
    assert response.json()["detail"] == "Error generating thumbnails: No such key"
