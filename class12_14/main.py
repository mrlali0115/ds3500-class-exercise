#main.py
import io
import logging
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import CSVInfo, DataStorage, MovieInput, MovieResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Movie API")

movies = {
    1: {"id": 1, "title": "Movie A", "release_year": 2020},
    2: {"id": 2, "title": "Movie B", "release_year": 2021},
}

storage = DataStorage()

@app.get("/health")
def health_check():
    return {"status": "ok"}

#a path parameter identifies a resource (movie) to retrieve
@app.get("/demo/movies/{movie_id}")
def demo_get_movie(movie_id: int):
    return {"requested_id": movie_id}

#a query parameter adjusts a request
@app.get("/demo/movies")
def demo_list_movies(limit: int = Query(default=2, ge=1)):
    return {"requested_limit": limit}

@app.post("/demo/movies")
def demo_add_movie(movie: MovieInput):
    return movie.model_dump()

demo_movie_examples = []

@app.post("/demo/movie-examples", response_model=MovieResponse)
def demo_add_movie_example(movie: MovieInput):
    movie_id = len(demo_movie_examples) + 1
    record = movie.model_dump()
    record["id"] = movie_id
    demo_movie_examples.append(record)
    return record

@app.get("/movies", response_model=list[MovieResponse])
def list_movies(limit: int = Query(default=2, ge=1)):
    result = list(movies.values())[:limit]
    logger.info(f"Returned {len(result)} movies")
    return result

@app.post("/movies", response_model=MovieResponse)
def add_movie(movie: MovieInput):
    movie_id = len(movies) + 1
    record = movie.model_dump()
    record["id"] = movie_id
    movies[movie_id] = record
    logger.info(f"Added movie: id={movie_id}")
    return record

@app.post("/demo/inspect-csv")
async def demo_inspect_csv(file: UploadFile = File(...)):
    # ... in File(...) means the upload is required.
    contents = await file.read()
    return {"filename": file.filename, "size_bytes": len(contents)}

@app.get("/demo/movie-lookup/{movie_id}", response_model=MovieResponse)
def demo_lookup_movie(movie_id: int):
    movie = movies.get(movie_id)

    if movie is None:
        logger.warning(f"Movie not found: {movie_id}")
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie

@app.post("/inspect-csv", response_model=CSVInfo)
async def inspect_csv(file: UploadFile = File(...)):
    extension = Path(file.filename or "").suffix.lower()
    if extension != ".csv":
        logger.warning(f"Unsupported file format: {extension}")
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {extension}")

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
        logger.warning(f"Cannot read CSV: {error}")
        raise HTTPException(status_code=400, detail="Cannot read the uploaded CSV")

    dataset_id = storage.save_data(df, file.filename)
    logger.info(f"Stored CSV: id={dataset_id}, filename={file.filename}")
    return CSVInfo(
        filename=file.filename,
        rows=df.shape[0],
        columns=df.shape[1],
        column_names=list(df.columns),
        dataset_id=dataset_id,
    )

@app.get("/datasets/{dataset_id}/shape")
def get_dataset_shape(dataset_id: int):
    df = storage.get_data(dataset_id)
    if df is None:
        logger.warning(f"Dataset not found: {dataset_id}")
        raise HTTPException(status_code=404, detail="Dataset not found")

    logger.info(f"Retrieved dataset shape: id={dataset_id}")
    return {"dataset_id": dataset_id, "rows": df.shape[0], "columns": df.shape[1]}
