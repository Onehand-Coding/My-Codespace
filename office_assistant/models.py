from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Resident(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class ServiceRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    resident_id: Optional[int] = Field(default=None, foreign_key="resident.id")
    category: str
    description: str
    status: str = "open"  # open, in_progress, closed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Permit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    resident_id: Optional[int] = Field(default=None, foreign_key="resident.id")
    type: str
    status: str = "pending"  # pending, approved, rejected
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    decided_at: Optional[datetime] = None


class Contact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    department: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    status: str = "todo"  # todo, in_progress, done
    notes: Optional[str] = None
