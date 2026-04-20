import uuid
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from database import get_db_session, PlannerItem, Hackathon

router = APIRouter(prefix="/api/planner", tags=["planner"])


class PlannerItemCreate(BaseModel):
    """Schema for creating a new planner item."""
    hackathon_id: str = Field(..., description="ID of the associated hackathon")
    session_id: str = Field(..., description="Session ID for anonymous user identification")
    title: str = Field(..., min_length=1, max_length=200, description="Title of the plan item")
    start_time: datetime = Field(..., description="Start time of the plan item")
    end_time: datetime = Field(..., description="End time of the plan item")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    type: Optional[str] = Field(None, description="Type of plan item (idea|build|submit|sleep|review|meeting)")
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code")


class PlannerItemUpdate(BaseModel):
    """Schema for updating a planner item."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Title of the plan item")
    start_time: Optional[datetime] = Field(None, description="Start time of the plan item")
    end_time: Optional[datetime] = Field(None, description="End time of the plan item")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    type: Optional[str] = Field(None, description="Type of plan item (idea|build|submit|sleep|review|meeting)")
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code")


class PlannerItemResponse(BaseModel):
    """Schema for planner item response."""
    id: str
    hackathon_id: str
    session_id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str]
    type: Optional[str]
    color: Optional[str]
    created_at: datetime


@router.get("/{hackathon_id}")
async def get_planner_items(
    hackathon_id: str,
    session_id: str = Query(..., description="Session ID for filtering user's plan items"),
    db: AsyncSession = Depends(get_db_session)
) -> List[PlannerItemResponse]:
    """
    Get all planner items for a specific hackathon and session.
    
    - **hackathon_id**: ID of the hackathon
    - **session_id**: Session ID to filter items for the current user
    """
    
    # Verify hackathon exists
    hackathon_query = select(Hackathon).where(Hackathon.id == hackathon_id)
    hackathon_result = await db.execute(hackathon_query)
    hackathon = hackathon_result.scalar_one_or_none()
    
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    
    # Get planner items for this hackathon and session
    query = select(PlannerItem).where(
        and_(
            PlannerItem.hackathon_id == hackathon_id,
            PlannerItem.session_id == session_id
        )
    ).order_by(PlannerItem.start_time.asc())
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return [
        PlannerItemResponse(
            id=item.id,
            hackathon_id=item.hackathon_id,
            session_id=item.session_id,
            title=item.title,
            start_time=item.start_time,
            end_time=item.end_time,
            description=item.description,
            type=item.type,
            color=item.color,
            created_at=item.created_at
        )
        for item in items
    ]


@router.post("")
async def create_planner_item(
    item_data: PlannerItemCreate,
    db: AsyncSession = Depends(get_db_session)
) -> PlannerItemResponse:
    """
    Create a new planner item.
    
    - **hackathon_id**: ID of the associated hackathon
    - **session_id**: Session ID for anonymous user identification
    - **title**: Title of the plan item
    - **start_time**: Start time of the plan item
    - **end_time**: End time of the plan item
    - **description**: Optional description
    - **type**: Type of plan item (idea|build|submit|sleep|review|meeting)
    - **color**: Hex color code for the item
    """
    
    # Verify hackathon exists
    hackathon_query = select(Hackathon).where(Hackathon.id == item_data.hackathon_id)
    hackathon_result = await db.execute(hackathon_query)
    hackathon = hackathon_result.scalar_one_or_none()
    
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    
    # Validate time range
    if item_data.start_time >= item_data.end_time:
        raise HTTPException(status_code=400, detail="Start time must be before end time")
    
    # Create new planner item
    new_item = PlannerItem(
        id=str(uuid.uuid4()),
        hackathon_id=item_data.hackathon_id,
        session_id=item_data.session_id,
        title=item_data.title,
        start_time=item_data.start_time,
        end_time=item_data.end_time,
        description=item_data.description,
        type=item_data.type,
        color=item_data.color
    )
    
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    
    return PlannerItemResponse(
        id=new_item.id,
        hackathon_id=new_item.hackathon_id,
        session_id=new_item.session_id,
        title=new_item.title,
        start_time=new_item.start_time,
        end_time=new_item.end_time,
        description=new_item.description,
        type=new_item.type,
        color=new_item.color,
        created_at=new_item.created_at
    )


@router.patch("/{item_id}")
async def update_planner_item(
    item_id: str,
    item_data: PlannerItemUpdate,
    db: AsyncSession = Depends(get_db_session)
) -> PlannerItemResponse:
    """
    Update an existing planner item.
    
    - **item_id**: ID of the planner item to update
    - **title**: New title (optional)
    - **start_time**: New start time (optional)
    - **end_time**: New end time (optional)
    - **description**: New description (optional)
    - **type**: New type (optional)
    - **color**: New color (optional)
    """
    
    # Get existing item
    query = select(PlannerItem).where(PlannerItem.id == item_id)
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Planner item not found")
    
    # Update fields if provided
    update_data = item_data.model_dump(exclude_unset=True)
    
    # Validate time range if both times are being updated or one is updated
    start_time = update_data.get('start_time', item.start_time)
    end_time = update_data.get('end_time', item.end_time)
    
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="Start time must be before end time")
    
    # Apply updates
    for field, value in update_data.items():
        setattr(item, field, value)
    
    await db.commit()
    await db.refresh(item)
    
    return PlannerItemResponse(
        id=item.id,
        hackathon_id=item.hackathon_id,
        session_id=item.session_id,
        title=item.title,
        start_time=item.start_time,
        end_time=item.end_time,
        description=item.description,
        type=item.type,
        color=item.color,
        created_at=item.created_at
    )


@router.delete("/{item_id}")
async def delete_planner_item(
    item_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Delete a planner item.
    
    - **item_id**: ID of the planner item to delete
    """
    
    # Get existing item
    query = select(PlannerItem).where(PlannerItem.id == item_id)
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Planner item not found")
    
    await db.delete(item)
    await db.commit()
    
    return {"message": "Planner item deleted successfully"}


def format_datetime_for_ics(dt: datetime) -> str:
    """Format datetime for ICS file format (YYYYMMDDTHHMMSSZ)."""
    return dt.strftime("%Y%m%dT%H%M%SZ")


def escape_ics_text(text: str) -> str:
    """Escape special characters for ICS format."""
    if not text:
        return ""
    
    # Escape special characters according to RFC 5545
    text = text.replace("\\", "\\\\")  # Backslash
    text = text.replace(",", "\\,")    # Comma
    text = text.replace(";", "\\;")    # Semicolon
    text = text.replace("\n", "\\n")   # Newline
    text = text.replace("\r", "")      # Remove carriage return
    
    return text


@router.get("/{hackathon_id}/export/ics")
async def export_planner_calendar(
    hackathon_id: str,
    session_id: str = Query(..., description="Session ID for filtering user's plan items"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Export planner items as ICS calendar file for a specific hackathon and session.
    
    - **hackathon_id**: ID of the hackathon
    - **session_id**: Session ID to filter items for the current user
    """
    
    # Verify hackathon exists
    hackathon_query = select(Hackathon).where(Hackathon.id == hackathon_id)
    hackathon_result = await db.execute(hackathon_query)
    hackathon = hackathon_result.scalar_one_or_none()
    
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    
    # Get planner items for this hackathon and session
    query = select(PlannerItem).where(
        and_(
            PlannerItem.hackathon_id == hackathon_id,
            PlannerItem.session_id == session_id
        )
    ).order_by(PlannerItem.start_time.asc())
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Generate ICS content
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//HackRadar//Planner//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{escape_ics_text(hackathon.title)} - HackRadar Planner",
        f"X-WR-CALDESC:Planner for {escape_ics_text(hackathon.title)} hackathon"
    ]
    
    # Add each planner item as an event
    for item in items:
        event_lines = [
            "BEGIN:VEVENT",
            f"UID:{item.id}@hackradar.com",
            f"DTSTAMP:{format_datetime_for_ics(datetime.utcnow())}",
            f"DTSTART:{format_datetime_for_ics(item.start_time)}",
            f"DTEND:{format_datetime_for_ics(item.end_time)}",
            f"SUMMARY:{escape_ics_text(item.title)}",
            f"DESCRIPTION:{escape_ics_text(item.description or '')}",
            f"CATEGORIES:{escape_ics_text(item.type or 'general')}",
            f"LOCATION:{escape_ics_text(hackathon.location or 'Online')}",
            "STATUS:CONFIRMED",
            "TRANSP:OPAQUE"
        ]
        
        # Add color if specified (as X-MICROSOFT-CDO-BUSYSTATUS for Outlook compatibility)
        if item.color:
            event_lines.append(f"X-MICROSOFT-CDO-BUSYSTATUS:BUSY")
            event_lines.append(f"X-OUTLOOK-COLOR:{item.color}")
        
        event_lines.append("END:VEVENT")
        ics_lines.extend(event_lines)
    
    ics_lines.append("END:VCALENDAR")
    
    # Join lines with CRLF as per RFC 5545
    ics_content = "\r\n".join(ics_lines)
    
    # Generate filename
    safe_hackathon_name = "".join(c for c in hackathon.title if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_hackathon_name = safe_hackathon_name.replace(' ', '_')
    filename = f"hackradar_planner_{safe_hackathon_name}.ics"
    
    # Return ICS file
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Cache-Control": "no-cache"
        }
    )