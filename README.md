# FastAPI OpenSearch PDF Search Application

This project is a FastAPI application that allows users to upload and index PDF files, enabling keyword searches within the content of the PDFs. The PDF files are indexed using OpenSearch, and users can search for specific keywords and see the sentences where the keywords appear.

## Features

- **PDF Upload:** Users can upload PDF files, and their contents are indexed in OpenSearch.
- **Keyword Search:** Users can search for specific keywords within the PDFs, and the sentences containing those keywords are displayed.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/username/repo-name.git
   cd repo-name

2. **Install the required Python packages:**

    pip install -r requirements.txt

3. **Start OpenSearch and OpenSearch Dashboards using Docker:** Use the docker-compose.yml file in the project to run OpenSearch and OpenSearch Dashboards:

    docker-compose up -d

4. **Create a .env file:** Create a .env file in the root directory of the project and add the following information:

    OPENSEARCH_HOST=localhost
    OPENSEARCH_PORT=9200
    OPENSEARCH_SCHEME=http

5. **Start the application:** Run the FastAPI application using Uvicorn:

    uvicorn main:app --reload

6. **Access the application:**

    Open your browser and visit http://localhost:8000 to use the application.

## Usage

**PDF Upload:**

Use the "Upload" button on the main page to upload a new PDF file.

**Keyword Search:**

Enter the keyword you want to search for in the search box and click the "Search" button.
The sentences containing the keyword will be displayed.

## Requirements

Python 3.7+
Docker
OpenSearch and OpenSearch Dashboards

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
