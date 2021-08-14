import urllib
import os

import sqlalchemy
from pydantic import BaseModel
import databases
from databases import *
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from typing import List
DATABASE_URL ="postgres://hhksqvonnypepj:c85c40b831b9442a3d3846f0e5016270754f22273ce056d5ea005d16c9556812@ec2-52-6-211-59.compute-1.amazonaws.com:5432/d9ldc3f53rdrdn"
#DATABASE_URL ="sqlite:///./test.db"

host_server = os.environ.get('host_server','localhost')
db_server_port= urllib.parse.quote_plus(str(os.environ.get('db_server_port','5432')))
database_name= os.environ.get('database_name','fastapi')
db_username= urllib.parse.quote_plus(str(os.environ.get('db_username','postgres')))
db_password= urllib.parse.quote_plus(str(os.environ.get('db_password','1234')))
ssl_mode= urllib.parse.quote_plus(str(os.environ.get('ssl_mode','prefer')))

#DATABASE_URL= 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(db_username,db_password,host_server,db_server_port,database_name,ssl_mode)

metadata = sqlalchemy.MetaData()


empleado = sqlalchemy.Table(
    'empleado',
    metadata,
    sqlalchemy.Column("id",sqlalchemy.Integer,primary_key=True),
    sqlalchemy.Column("nombre",sqlalchemy.String),
    sqlalchemy.Column("apellido",sqlalchemy.String),
    sqlalchemy.Column("status",sqlalchemy.Boolean),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL,pool_size=3, max_overflow=0
)
metadata.create_all(engine)



class EmpleadoIn(BaseModel):
    nombre:str
    apellido:str
    status: bool

class Empleado(BaseModel):
    id: int
    nombre:str
    apellido:str
    status: bool




app = FastAPI(title="FAST API UMG ")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


database = databases.Database(DATABASE_URL)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnet()

@app.post("/empleados/",response_model=Empleado)
async def create_empleado(emp:EmpleadoIn):
    query= empleado.insert().values(nombre=emp.nombre,apellido=emp.apellido, status=emp.status)
    
    last_record_id =await database.execute(query)
    return {**emp.dict(), "id":last_record_id}

@app.get("/getEmpleado/",response_model=List[Empleado] )
async def getEmpleado(skip: int=0, take: int=20):
    query= empleado.select().offset(skip).limit(take)
    return await database.fetch_all(query)



@app.get("/getEmpleado/{empleado_id}",response_model=Empleado)
async def getEmpleadoId(emp_id: int ):
    query= empleado.select().where(empleado.c.id==emp_id  )
    return await database.fetch_one(query)

@app.delete("/empleadoDelete/{empleado_id}/")
async def del_empleado(emp_id: int):
    query = empleado.delete().where(empleado.c.id==emp_id)
    await database.execute(query)
    return {"message":" Empleado with id:{} deleted succesfully!".format(emp_id)}

@app.put("/empleadoUpdate/{emp_id}",response_model=Empleado)
async def setEmpleadoId(emp_id: int,emp:EmpleadoIn):
    query = empleado.update().where(empleado.c.id==emp_id).values(nombre=emp.nombre, apellido=emp.apellido,status=emp.status)
    await database.execute(query)
    return {**emp.dict(),"id":emp_id}


