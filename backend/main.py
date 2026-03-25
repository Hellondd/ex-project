from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # Импортируем для статики
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from datetime import date, time
import os

# База данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Workspace(Base):
    __tablename__ = "workspaces"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(String)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    user_id = Column(Integer)
    book_date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# 1. Сначала идут API роутеры
@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    if not db.query(Workspace).first():
        db.add_all([
            Workspace(name="Meeting Room A", type="room"), 
            Workspace(name="Desk 01", type="desk"),
            Workspace(name="Desk 02", type="desk")
        ])
        db.commit()
    db.close()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

class BookingCreate(BaseModel):
    workspace_id: int
    user_id: int
    book_date: date
    start_time: time
    end_time: time

@app.get("/api/workspaces") # Добавили префикс /api для ясности
def list_workspaces(db: Session = Depends(get_db)):
    return db.query(Workspace).all()

@app.post("/api/bookings")
def make_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    overlap = db.query(Booking).filter(
        Booking.workspace_id == booking.workspace_id,
        Booking.book_date == booking.book_date,
        Booking.start_time < booking.end_time,
        Booking.end_time > booking.start_time
    ).first()
    if overlap: raise HTTPException(status_code=400, detail="Slot occupied")
    new_b = Booking(**booking.dict())
    db.add(new_b)
    db.commit()
    return {"status": "success"}

# 2. ПОДКЛЮЧЕНИЕ СТАТИКИ (Frontend)
# Указываем путь к папке frontend, которая находится на одном уровне с папкой backend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")

# Монтируем папку для доступа к CSS и JS
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Роут для отдачи главного index.html по адресу http://127.0.0.1:8000/
@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))