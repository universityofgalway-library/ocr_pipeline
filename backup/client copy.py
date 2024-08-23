import boto3

# Create a Textract client
client = boto3.client('textract')

# Path to the image file
file_path = r"Z:\OCR outputs\p155_kerby_miller\Letters\ocr_test\testing.jpg"

# Open the image file
with open(file_path, 'rb') as document:
    # Call Textract to analyze the document
    response = client.detect_document_text(
        Document={'Bytes': document.read()}
    )

# Print the detected text
for item in response['Blocks']:
    if item['BlockType'] == 'LINE':
        print(item['Text'])
