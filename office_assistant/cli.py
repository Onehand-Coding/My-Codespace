from __future__ import annotations
import json
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from sqlmodel import select

from .db import init_db, get_session
from .models import Resident, ServiceRequest, Permit, Contact, Task

app = typer.Typer(help="Municipal Assistant CLI")
console = Console()


@app.callback()
def main() -> None:
    """Initialize database on first run."""
    init_db()


# Residents
resident_app = typer.Typer(help="Manage residents")
app.add_typer(resident_app, name="resident")


@resident_app.command("add")
def resident_add(name: str, email: Optional[str] = None, phone: Optional[str] = None, address: Optional[str] = None) -> None:
    with next(get_session()) as session:
        resident = Resident(name=name, email=email, phone=phone, address=address)
        session.add(resident)
        session.commit()
        session.refresh(resident)
        console.print(f"Added resident [bold]{resident.name}[/bold] (id={resident.id})")


@resident_app.command("list")
def resident_list() -> None:
    with next(get_session()) as session:
        residents = session.exec(select(Resident)).all()
        table = Table(title="Residents")
        table.add_column("ID", justify="right")
        table.add_column("Name")
        table.add_column("Email")
        table.add_column("Phone")
        table.add_column("Address")
        for r in residents:
            table.add_row(str(r.id), r.name, r.email or "", r.phone or "", r.address or "")
        console.print(table)


# Service Requests
sr_app = typer.Typer(help="Manage service requests")
app.add_typer(sr_app, name="sr")


@sr_app.command("open")
def sr_open(resident_id: Optional[int] = typer.Option(None), category: str = typer.Option(...), description: str = typer.Option(...)) -> None:
    with next(get_session()) as session:
        sr = ServiceRequest(resident_id=resident_id, category=category, description=description)
        session.add(sr)
        session.commit()
        session.refresh(sr)
        console.print(f"Opened SR id={sr.id} category={sr.category}")


@sr_app.command("list")
def sr_list(status: Optional[str] = None) -> None:
    with next(get_session()) as session:
        query = select(ServiceRequest)
        if status:
            query = query.where(ServiceRequest.status == status)
        srs = session.exec(query.order_by(ServiceRequest.created_at.desc())).all()
        table = Table(title="Service Requests")
        table.add_column("ID", justify="right")
        table.add_column("ResidentID", justify="right")
        table.add_column("Category")
        table.add_column("Status")
        table.add_column("Created")
        for s in srs:
            table.add_row(str(s.id), str(s.resident_id or ""), s.category, s.status, s.created_at.strftime("%Y-%m-%d"))
        console.print(table)


@sr_app.command("update")
def sr_update(sr_id: int, status: str) -> None:
    with next(get_session()) as session:
        sr = session.get(ServiceRequest, sr_id)
        if not sr:
            raise typer.Exit(code=1)
        sr.status = status
        sr.updated_at = datetime.utcnow()
        session.add(sr)
        session.commit()
        console.print(f"Updated SR id={sr.id} -> status={sr.status}")


# Permits
permit_app = typer.Typer(help="Manage permits")
app.add_typer(permit_app, name="permit")


@permit_app.command("apply")
def permit_apply(resident_id: Optional[int] = None, type: str = typer.Option(..., help="Permit type")) -> None:
    with next(get_session()) as session:
        permit = Permit(resident_id=resident_id, type=type)
        session.add(permit)
        session.commit()
        session.refresh(permit)
        console.print(f"Permit submitted id={permit.id} type={permit.type}")


@permit_app.command("decide")
def permit_decide(permit_id: int, outcome: str = typer.Option(..., help="approved/rejected")) -> None:
    with next(get_session()) as session:
        permit = session.get(Permit, permit_id)
        if not permit:
            raise typer.Exit(code=1)
        permit.status = "approved" if outcome == "approved" else "rejected"
        permit.decided_at = datetime.utcnow()
        session.add(permit)
        session.commit()
        console.print(f"Permit id={permit.id} -> {permit.status}")


@permit_app.command("list")
def permit_list(status: Optional[str] = None) -> None:
    with next(get_session()) as session:
        query = select(Permit)
        if status:
            query = query.where(Permit.status == status)
        permits = session.exec(query.order_by(Permit.submitted_at.desc())).all()
        table = Table(title="Permits")
        table.add_column("ID", justify="right")
        table.add_column("ResidentID", justify="right")
        table.add_column("Type")
        table.add_column("Status")
        table.add_column("Submitted")
        for p in permits:
            table.add_row(str(p.id), str(p.resident_id or ""), p.type, p.status, p.submitted_at.strftime("%Y-%m-%d"))
        console.print(table)


# Contacts
contact_app = typer.Typer(help="Department contacts")
app.add_typer(contact_app, name="contact")


@contact_app.command("add")
def contact_add(department: str, name: str, email: Optional[str] = None, phone: Optional[str] = None) -> None:
    with next(get_session()) as session:
        contact = Contact(department=department, name=name, email=email, phone=phone)
        session.add(contact)
        session.commit()
        session.refresh(contact)
        console.print(f"Added contact id={contact.id} for {department}")


@contact_app.command("list")
def contact_list(department: Optional[str] = None) -> None:
    with next(get_session()) as session:
        query = select(Contact)
        if department:
            query = query.where(Contact.department == department)
        contacts = session.exec(query).all()
        table = Table(title="Contacts")
        table.add_column("ID", justify="right")
        table.add_column("Dept")
        table.add_column("Name")
        table.add_column("Email")
        table.add_column("Phone")
        for c in contacts:
            table.add_row(str(c.id), c.department, c.name, c.email or "", c.phone or "")
        console.print(table)


# Tasks
task_app = typer.Typer(help="Tasks and follow-ups")
app.add_typer(task_app, name="task")


@task_app.command("add")
def task_add(title: str, due: Optional[str] = typer.Option(None, help="YYYY-MM-DD"), assigned_to: Optional[str] = None, notes: Optional[str] = None) -> None:
    due_date = None
    if due:
        due_date = datetime.strptime(due, "%Y-%m-%d")
    with next(get_session()) as session:
        task = Task(title=title, due_date=due_date, assigned_to=assigned_to, notes=notes)
        session.add(task)
        session.commit()
        session.refresh(task)
        console.print(f"Added task id={task.id} -> {task.title}")


@task_app.command("list")
def task_list(status: Optional[str] = None) -> None:
    with next(get_session()) as session:
        query = select(Task)
        if status:
            query = query.where(Task.status == status)
        tasks = session.exec(query).all()
        table = Table(title="Tasks")
        table.add_column("ID", justify="right")
        table.add_column("Title")
        table.add_column("Due")
        table.add_column("Assigned")
        table.add_column("Status")
        for t in tasks:
            table.add_row(str(t.id), t.title, t.due_date.strftime("%Y-%m-%d") if t.due_date else "", t.assigned_to or "", t.status)
        console.print(table)


@task_app.command("update")
def task_update(task_id: int, status: str) -> None:
    with next(get_session()) as session:
        task = session.get(Task, task_id)
        if not task:
            raise typer.Exit(code=1)
        task.status = status
        session.add(task)
        session.commit()
        console.print(f"Task id={task.id} -> {task.status}")


# Export
@app.command("export")
def export_json(output: str = typer.Option("data/export.json", "--output", "-o")) -> None:
    with next(get_session()) as session:
        data = {
            "residents": [r.model_dump() for r in session.exec(select(Resident)).all()],
            "service_requests": [s.model_dump() for s in session.exec(select(ServiceRequest)).all()],
            "permits": [p.model_dump() for p in session.exec(select(Permit)).all()],
            "contacts": [c.model_dump() for c in session.exec(select(Contact)).all()],
            "tasks": [t.model_dump() for t in session.exec(select(Task)).all()],
        }
        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, default=str, indent=2)
    console.print(f"Exported data to {output}")


if __name__ == "__main__":
    app()
