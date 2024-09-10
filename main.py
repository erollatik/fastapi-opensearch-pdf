from fastapi import FastAPI, File, UploadFile, Request
from fastapi.templating import Jinja2Templates
from opensearchpy import OpenSearch, helpers
import os
import re
from dotenv import load_dotenv
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

# env variables
load_dotenv()

# OpenSearch connection
opensearch_host = os.getenv("OPENSEARCH_HOST")
opensearch_port = int(os.getenv("OPENSEARCH_PORT"))
opensearch_scheme = os.getenv("OPENSEARCH_SCHEME")

app = FastAPI()

# OpenSearch client
es = OpenSearch(
    hosts=[{'host': opensearch_host, 'port': opensearch_port, 'scheme': opensearch_scheme}]
)

if es.ping():
    print("Connected to OpenSearch!")
else:
    print("Couldn't connect to OpenSearch")

index_name = 'articles'

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)
    print(f"Index '{index_name}' created.")
else:
    print(f"Index '{index_name}' already exists.")

# Refresh interval off
es.indices.put_settings(
    index=index_name,
    body={"index": {"refresh_interval": "-1"}}
)

templates = Jinja2Templates(directory="templates")


def extract_text_with_pymupdf(file_path):
    try:
        with fitz.open(file_path) as pdf:
            text = ''
            for page_num in range(pdf.page_count):
                page = pdf[page_num]
                page_text = page.get_text()
                if page_text:
                    text += page_text
                else:
                    print(f"Warning: Page {page_num + 1} could not be extracted properly.")
            return text
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return ''


def ocr_on_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error processing OCR on {image_path}: {e}")
        return ''


# Upload pdf
@app.post("/upload/")
async def upload_files(pdf_files: list[UploadFile] = File(...)):
    bulk_actions = []  # Bulk lists

    for pdf_file in pdf_files:
        file_location = f"./{pdf_file.filename}"

        with open(file_location, "wb+") as file_object:
            file_object.write(pdf_file.file.read())

        text = extract_text_with_pymupdf(file_location)

        if not text.strip():
            print(f"Trying OCR for {pdf_file.filename} due to missing text.")
            text = ocr_on_image(file_location)

        if text.strip():
            article = {
                'title': pdf_file.filename,
                'content': text
            }

            action = {
                "_op_type": "index",
                "_index": index_name,
                "_source": article
            }
            bulk_actions.append(action)
        else:
            print(f"No valid text found in {pdf_file.filename}")

        os.remove(file_location)

    if bulk_actions:
        try:
            helpers.bulk(es, bulk_actions)
            print("Bulk indexing successful.")
        except Exception as e:
            print(f"Error during bulk indexing: {e}")

    # Manual refreshing
    es.indices.refresh(index=index_name)
    print("Manual refresh performed after indexing.")

    return {"message": f"{len(pdf_files)} files uploaded successfully"}


@app.on_event("shutdown")
def reset_refresh_interval():
    es.indices.put_settings(
        index=index_name,
        body={"index": {"refresh_interval": "1s"}}
    )


@app.get("/search/")
async def search_articles(request: Request, query: str = "", size: int = 100):
    results = []
    if query:
        search_query = {
            "query": {
                "match": {
                    "content": {
                        "query": query,
                        "operator": "and",
                        "fuzziness": "AUTO"
                    }
                }
            },
            "size": size
        }

        response = es.search(index=index_name, body=search_query)
        for hit in response['hits']['hits']:
            title = hit["_source"]["title"]
            content = hit["_source"]["content"]

            # Metni cümlelere böl ve sorgu terimini içeren cümleleri bul
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content)

            for sentence in sentences:
                if query.lower() in sentence.lower():
                    results.append({"title": title, "highlighted_text": sentence.strip()})

    return templates.TemplateResponse("search.html", {"request": request, "query": query, "results": results})

# pip install -r requirements.txt
# uvicorn main:app --reload
# http://localhost:8000/search/?query
