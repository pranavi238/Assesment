# REST Thumbnail Creation Service

This project is a Python-based REST API built with **FastAPI** that accepts one or more image uploads, generates resized thumbnails using presets or custom dimensions, and returns metadata and retrievable thumbnail URLs.

##  stack

- FastAPI (Python 3)
- Uvicorn ASGI server
- Pillow for image processing
- Pytest for testing



## Running the service

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open the automatic docs:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Testing

```bash
pytest
```

## Basic usage

Once running, you will be able to:

- Upload one or more images to generate thumbnails
- Use either preset sizes (small, medium, large) or custom width/height
- Retrieve generated thumbnails by ID

## API

- **Health check**
  - **GET** `/health`


- **Create thumbnails**
  - **POST** `/thumbnails`
  - **Request**: `multipart/form-data`
    - `files`: one or more image files (`image/jpeg`, `image/png`, `image/webp`).
  - **Response**: `201 Created` with a JSON array of thumbnail metadata:

- **Retrieve thumbnail**
  - **GET** `/thumbnails/{id}`
 
