"""Development-only FastAPI ingestion/query API, SQLite demo persistence.

NOT authenticated or rate limited. Bind to localhost in development; do not
expose on a public network, or integrate with industrial equipment, without
auth, HTTPS, authorization, operational security review and permissions.
"""
from __future__ import annotations
from contextlib import closing
import os
from pathlib import Path
import sqlite3
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, ConfigDict
from .engine import SPECS,generate,ingest,connect,read_events,analyze

class Event(BaseModel):
    model_config=ConfigDict(extra="forbid")
    event_id:str=Field(min_length=6,max_length=80)
    project_id:int=Field(ge=91,le=100)
    sequence:int=Field(ge=1)
    occurred_at:str
    payload:dict
    origin:str
    schema_version:int=Field(ge=1,le=1)

class EventBatch(BaseModel):
    events:list[Event]=Field(min_length=1,max_length=2000)

def create_app(db_path:str|None=None)->FastAPI:
    path=db_path or os.environ.get("ADVANCED_DB_PATH","/tmp/advanced-industrial-demo.sqlite3")
    app=FastAPI(title="Advanced Industrial Demo API",version="0.1.0",
        description="Exclusively synthetic projects #091-100. Not a production industrial or safety system.")
    with closing(connect(path)):pass

    @app.get("/health")
    def health():
        return {"status":"ok","mode":"synthetic-demo","external_services_verified":False}

    @app.get("/v1/projects")
    def projects():
        return [{"project_id":k,**v} for k,v in SPECS.items()]

    @app.post("/v1/projects/{project}/simulate")
    def simulate(project:int,count:int=Query(96,ge=24,le=2000)):
        if project not in SPECS:raise HTTPException(status_code=404,detail="Unknown project")
        try:
            events=generate(project,count=count)
            with closing(connect(path)) as db:summary=ingest(db,events)
        except ValueError as exc:
            raise HTTPException(status_code=422,detail=str(exc)) from exc
        return {"project_id":project,**summary,"data_origin":"SYNTHETIC"}

    @app.post("/v1/projects/{project}/ingest")
    def write_events(project:int,batch:EventBatch):
        if project not in SPECS:raise HTTPException(status_code=404,detail="Unknown project")
        events=[x.model_dump() for x in batch.events]
        if any(e["project_id"]!=project for e in events):
            raise HTTPException(status_code=422,detail="Mixed projects")
        try:
            with closing(connect(path)) as db:out=ingest(db,events)
        except (ValueError,sqlite3.IntegrityError) as exc:
            raise HTTPException(status_code=409,detail=str(exc)) from exc
        return out

    @app.get("/v1/projects/{project}/events")
    def events(project:int,limit:int=Query(100,ge=1,le=2000)):
        if project not in SPECS:raise HTTPException(status_code=404,detail="Unknown project")
        with closing(connect(path)) as db:rows=read_events(db,project,limit)
        return {"project_id":project,"count":len(rows),"events":rows}

    @app.get("/v1/projects/{project}/analytics")
    def analytics(project:int):
        if project not in SPECS:raise HTTPException(status_code=404,detail="Unknown project")
        with closing(connect(path)) as db:rows=read_events(db,project,2000)
        if len(rows)<24:
            raise HTTPException(status_code=409,detail="Ingest at least 24 demo events first")
        try:return analyze(project,rows)
        except ValueError as exc:raise HTTPException(status_code=422,detail=str(exc)) from exc

    return app

# Imported lazily by uvicorn: advanced_batch.api:app
app=create_app()

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8000)
