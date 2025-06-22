# Author-Co-Author Network Navigator

This project provides a web-based interface to explore a network of academic authors and their co-authors. It features a semantic search engine to find authors based on their research abstracts and a 3D force-directed graph to visualize the co-authorship network.

## Features

*   **Semantic Search**: Find authors based on natural language queries related to their research.
*   **AI-Powered Explanations**: Get AI-generated explanations of why an author is a good match for your search query.
*   **3D Network Visualization**: Explore the co-authorship network in an interactive 3D graph.
*   **Flask-Based API**: A simple and extensible API for search and data retrieval.

## Prerequisites

Before you begin, ensure you have the following installed:

*   Python 3.7+
*   pip (Python package installer)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Key:**
    *   Rename the `config.env.example` file to `config.env`.
    *   Open `config.env` and add your Google Gemini API key:
        ```
        GOOGLE_API_KEY=your_google_api_key
        ```

## Data Preparation

The search engine and graph visualization rely on pre-processed data files.

1.  **Input Data:**
    The primary data source is a JSON file containing author information, including abstracts and co-author relationships. The project expects this file at `nicolasdata/author_abstracts_5.json`.

2.  **Generate Vector Database:**
    Run the `embedding_database.py` script to create the vector database from your input data. This will generate the `static/vectorbig.json` file by default.
    ```bash
    python embedding_database.py load nicolasdata/author_abstracts_5.json
    ```
    You can specify a different path for the database:
    ```bash
    python embedding_database.py --db /path/to/your/vector_database.json load nicolasdata/author_abstracts_5.json
    ```

3.  **Generate Force Graph Data:**
    Run the `convert_author_abstracts_4_to_graph.py` script to create the data for the 3D visualization. This will generate the `static/forcegraph_data_3.json` file. Provide the input and output file paths as arguments.
    ```bash
    python convert_author_abstracts_4_to_graph.py nicolasdata/author_abstracts_5.json static/forcegraph_data_3.json
    ```

## Running the Application

Once the data preparation is complete, you can start the web server:
```bash
python search_api.py
```

By default, the server runs on `0.0.0.0:5000` and uses the vector database at `static/vectorbig.json`. You can change the host, port, and database path using command-line arguments:
```bash
python search_api.py --host 127.0.0.1 --port 8080 --db /path/to/your/vector_database.json
```

The application will be available at `http://<host>:<port>`.

*   The 3D graph visualization will be at the root URL: `http://<host>:<port>/`
*   The search API is available at the `/search` endpoint.

## API Endpoints

### `/search`

*   **Method**: `POST`
*   **Description**: Performs a semantic search for authors based on a query.
*   **Body**:
    ```json
    {
        "query": "your search query here"
    }
    ```
*   **Response**: A JSON object with a list of matching authors.

### `/explain_match`

*   **Method**: `POST`
*   **Description**: Generates an AI-powered explanation for why an author matches a search query.
*   **Body**:
    ```json
    {
        "query": "your search query here",
        "author_id": "author_id_from_search_results"
    }
    ```
*   **Response**: A JSON object with the explanation text. 