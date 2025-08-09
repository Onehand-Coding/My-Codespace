from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import select

from .db import get_session, init_db
from .models import Resident, ServiceRequest, Permit, Contact, Task

app = FastAPI(title="Municipal Assistant API")


class ResidentIn(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.post("/residents", response_model=Resident)
def create_resident(payload: ResidentIn) -> Resident:
    with next(get_session()) as session:
        resident = Resident(**payload.model_dump())
        session.add(resident)
        session.commit()
        session.refresh(resident)
        return resident


@app.get("/residents", response_model=List[Resident])
def list_residents() -> List[Resident]:
    with next(get_session()) as session:
        return session.exec(select(Resident)).all()


class SRIn(BaseModel):
    resident_id: Optional[int] = None
    category: str
    description: str


@app.post("/service-requests", response_model=ServiceRequest)
def open_sr(payload: SRIn) -> ServiceRequest:
    with next(get_session()) as session:
        sr = ServiceRequest(**payload.model_dump())
        session.add(sr)
        session.commit()
        session.refresh(sr)
        return sr


@app.get("/service-requests", response_model=List[ServiceRequest])
def list_srs(status: Optional[str] = None) -> List[ServiceRequest]:
    with next(get_session()) as session:
        query = select(ServiceRequest)
        if status:
            query = query.where(ServiceRequest.status == status)
        return session.exec(query).all()


class PermitIn(BaseModel):
    resident_id: Optional[int] = None
    type: str


@app.post("/permits", response_model=Permit)
def create_permit(payload: PermitIn) -> Permit:
    with next(get_session()) as session:
        permit = Permit(**payload.model_dump())
        session.add(permit)
        session.commit()
        session.refresh(permit)
        return permit


@app.post("/permits/{permit_id}/decide", response_model=Permit)
def decide_permit(permit_id: int, outcome: str) -> Permit:
    with next(get_session()) as session:
        permit = session.get(Permit, permit_id)
        if not permit:
            raise HTTPException(404, "Permit not found")
        permit.status = "approved" if outcome == "approved" else "rejected"
        permit.decided_at = datetime.utcnow()
        session.add(permit)
        session.commit()
        session.refresh(permit)
        return permit


@app.get("/permits", response_model=List[Permit])
def list_permits(status: Optional[str] = None) -> List[Permit]:
    with next(get_session()) as session:
        query = select(Permit)
        if status:
            query = query.where(Permit.status == status)
        return session.exec(query).all()


class ContactIn(BaseModel):
    department: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None


@app.post("/contacts", response_model=Contact)
def create_contact(payload: ContactIn) -> Contact:
    with next(get_session()) as session:
        contact = Contact(**payload.model_dump())
        session.add(contact)
        session.commit()
        session.refresh(contact)
        return contact


@app.get("/contacts", response_model=List[Contact])
def list_contacts(department: Optional[str] = None) -> List[Contact]:
    with next(get_session()) as session:
        query = select(Contact)
        if department:
            query = query.where(Contact.department == department)
        return session.exec(query).all()


class TaskIn(BaseModel):
    title: str
    due: Optional[str] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


@app.post("/tasks", response_model=Task)
def create_task(payload: TaskIn) -> Task:
    with next(get_session()) as session:
        due_date = None
        if payload.due:
            due_date = datetime.strptime(payload.due, "%Y-%m-%d")
        task = Task(title=payload.title, due_date=due_date, assigned_to=payload.assigned_to, notes=payload.notes)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


@app.get("/tasks", response_model=List[Task])
def list_tasks(status: Optional[str] = None) -> List[Task]:
    with next(get_session()) as session:
        query = select(Task)
        if status:
            query = query.where(Task.status == status)
        return session.exec(query).all()
