# Tool Semantic Search (With CRUD Implementation)

A **FastAPI-based backend service** that manages tool details and provides **semantic search functionality** using PostgreSQL for structured data and Qdrant for similarity search.

---

## 🚀 Features

* **CRUD Operations**: Full Create, Read, Update, Delete functionality for tool management
* **Dual Database Storage**: Tools stored in PostgreSQL (structured data) + Qdrant (vector embeddings)
* **Semantic Search**: Find tools based on meaning, not just keywords
* **Search History**: Automatic logging of queries and results
* **RESTful API**: Clean design with proper HTTP status codes and error handling

---

## 🛠 Technology Stack

* **Framework**: FastAPI
* **Database**: PostgreSQL
* **Vector Database**: Qdrant
* **Embeddings**: [SentenceTransformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`)
* **API Docs**: Auto-generated Swagger UI & ReDoc

---

## 📂 Project Structure

```
tool-semantic-search/
├── app/
│   ├── config.py          # App configuration & settings
│   ├── crud.py            # Database operations
│   ├── database.py        # DB connection & initialization
│   ├── main.py            # FastAPI app & endpoints
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   └── vector_db.py       # Qdrant operations
├── init_db.py             # Database initialization script
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables
```

---

## 📋 Prerequisites

* Python 3.8+
* PostgreSQL
* Qdrant (via Docker)
* Git

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/onkars2006/tool-crud-semantic-search-api.git
cd tool-crud-semantic-search-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Databases

**PostgreSQL Setup**

* Install PostgreSQL
* Create a database named `tool_db`
* Update `.env` with your credentials:

```env
DATABASE_URL=postgresql://username:password@localhost/tool_db
```

**Qdrant Setup (Docker)**

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 5. Configure Environment

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://postgres:password@localhost/tool_db
QDRANT_URL=http://localhost:6333
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 6. Initialize Database

```bash
python init_db.py
```

This will:

* Create tables in PostgreSQL
* Reset sequences
* Create Qdrant collection

### 7. Start Application

```bash
uvicorn app.main:app --reload
```

App available at: [http://localhost:8000](http://localhost:8000)

---

## 📖 API Documentation

* **Swagger UI** → [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
* **ReDoc** → [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)

---

## 🔗 API Endpoints

### Tools Management

* `GET /api/v1/tools` → Retrieve all tools (pagination)
* `GET /api/v1/tools/{tool_id}` → Get tool by ID
* `POST /api/v1/tools` → Create new tool
* `PUT /api/v1/tools/{tool_id}` → Update tool
* `DELETE /api/v1/tools/{tool_id}` → Delete tool

### Search

* `POST /api/v1/search` → Perform semantic search
* `GET /api/v1/search/history` → Get search history

### Health Check

* `GET /api/v1/health` → Check API health

---

## 📝 Usage Examples

**Create a Tool**

```bash
curl -X POST "http://localhost:8000/api/v1/tools" -H "Content-Type: application/json" -d "{\"name\": \"Pandas\", \"description\": \"Python data analysis library\", \"tags\": [\"data-analysis\", \"python\", \"data-science\"], \"tool_metadata\": {\"category\": \"data-analysis\"}}"
```

**Get All Tools**

```bash
curl "http://localhost:8000/api/v1/tools"
```

**Get Specific Tool**

```bash
curl "http://localhost:8000/api/v1/tools/1"
```

**Update Tool**

```bash
curl -X PUT "http://localhost:8000/api/v1/tools/1" -H "Content-Type: application/json" -d "{\"name\": \"Pandas Library\", \"description\": \"Enhanced Python data analysis library\", \"tags\": [\"data-analysis\", \"python\", \"data-science\", \"updated\"], \"tool_metadata\": {\"category\": \"data-analysis\", \"version\": \"2.0\"}}"
```
**Delete a Tool**

```bash
curl -X DELETE "http://localhost:8000/api/v1/tools/1"
```

**Semantic Search**

```bash
curl -X POST "http://localhost:8000/api/v1/search" -H "Content-Type: application/json" -d "{\"query\": \"tools for data analysis\", \"limit\": 5}"
```

**Get Search History**

```bash
curl "http://localhost:8000/api/v1/search/history"
```

**Health Check**

```bash
curl "http://localhost:8000/api/v1/health"
```

---

## 🗄 Code Overview

### Database Models

* **Tool**

  * `id`, `name`, `description`, `tags`, `tool_metadata`
  * `created_at`, `updated_at`

* **SearchHistory**

  * `id`, `query`, `results`, `created_at`

### Vector Database Integration

* Tool data → embeddings (via SentenceTransformers)
* Stored in Qdrant with tool ID reference
* Queries → embeddings → similarity-ranked results

---


### Demo Video Working

[Demo Video](https://drive.google.com/file/d/1ike6e2TkhUSwNkEVEHOEWdfsq1itl0k5/view?usp=sharing)

* https://drive.google.com/file/d/1ike6e2TkhUSwNkEVEHOEWdfsq1itl0k5/view
