from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, String
from sqlalchemy.orm import selectinload
import json

from database import get_db_session, Hackathon

router = APIRouter(prefix="/api/hackathons", tags=["hackathons"])


@router.get("")
async def list_hackathons(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    source: Optional[str] = Query(None, description="Filter by source platform"),
    mode: Optional[str] = Query(None, description="Filter by mode (online/offline/hybrid)"),
    status: Optional[str] = Query(None, description="Filter by status (upcoming/ongoing/past)"),
    location: Optional[str] = Query(None, description="Filter by location (partial match)"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    sort_by: str = Query("start_date", description="Sort by field (start_date/deadline/recently_added)"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get paginated list of hackathons with filtering and sorting options.
    
    - **page**: Page number (1-based)
    - **limit**: Number of items per page (1-100)
    - **source**: Filter by source platform (devpost, mlh, hackerearth, etc.)
    - **mode**: Filter by mode (online, offline, hybrid)
    - **status**: Filter by status (upcoming, ongoing, past)
    - **location**: Filter by location (case-insensitive partial match)
    - **tag**: Filter by tag (case-insensitive partial match)
    - **search**: Search in title and description (case-insensitive)
    - **sort_by**: Sort by field (start_date, deadline, recently_added)
    """
    
    # Build base query
    query = select(Hackathon)
    
    # Apply filters
    filters = []
    
    if source:
        filters.append(Hackathon.source == source)
    
    if mode:
        filters.append(Hackathon.mode == mode)
    
    if status:
        # "open" means registrations are open (upcoming or ongoing)
        if status == "open":
            filters.append(or_(Hackathon.status == "upcoming", Hackathon.status == "ongoing"))
        else:
            filters.append(Hackathon.status == status)
    
    if location:
        # Filter by location using case-insensitive partial match
        filters.append(func.lower(Hackathon.location).contains(func.lower(location)))
    
    if tag:
        # Filter by tag using JSON contains (works for both SQLite and PostgreSQL)
        filters.append(func.json_extract(Hackathon.tags, '$') != None)
        # For more precise tag filtering, we'll use a text search approach
        filters.append(func.lower(func.cast(Hackathon.tags, String)).contains(func.lower(tag)))
    
    if search:
        search_term = f"%{search.lower()}%"
        filters.append(
            or_(
                func.lower(Hackathon.title).contains(search_term),
                func.lower(Hackathon.description).contains(search_term)
            )
        )
    
    if filters:
        query = query.where(and_(*filters))
    
    # Apply sorting
    if sort_by == "start_date":
        query = query.order_by(Hackathon.start_date.asc())
    elif sort_by == "deadline":
        query = query.order_by(Hackathon.registration_deadline.asc())
    elif sort_by == "recently_added":
        query = query.order_by(Hackathon.scraped_at.desc())
    else:
        # Default to start_date if invalid sort_by provided
        query = query.order_by(Hackathon.start_date.asc())
    
    # Get total count for pagination metadata
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total_count = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    hackathons = result.scalars().all()
    
    # Calculate pagination metadata
    total_pages = (total_count + limit - 1) // limit  # Ceiling division
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "hackathons": [
            {
                "id": h.id,
                "title": h.title,
                "source": h.source,
                "url": h.url,
                "image_url": h.image_url,
                "description": h.description,
                "prize_pool": h.prize_pool,
                "location": h.location,
                "mode": h.mode,
                "tags": json.loads(h.tags) if h.tags else [],
                "team_size_min": h.team_size_min,
                "team_size_max": h.team_size_max,
                "registration_deadline": h.registration_deadline.isoformat() if h.registration_deadline else None,
                "start_date": h.start_date.isoformat() if h.start_date else None,
                "end_date": h.end_date.isoformat() if h.end_date else None,
                "status": h.status,
                "scraped_at": h.scraped_at.isoformat() if h.scraped_at else None
            }
            for h in hackathons
        ],
        "total": total_count,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        }
    }


@router.get("/stats")
async def get_hackathon_stats(db: AsyncSession = Depends(get_db_session)):
    """
    Get hackathon statistics including total and registrations open counts.
    """
    
    # Get total count
    total_query = select(func.count(Hackathon.id))
    total_result = await db.execute(total_query)
    total_count = total_result.scalar()
    
    # Get registrations open count (upcoming + ongoing)
    open_query = select(func.count(Hackathon.id)).where(
        or_(Hackathon.status == "upcoming", Hackathon.status == "ongoing")
    )
    open_result = await db.execute(open_query)
    open_count = open_result.scalar()
    
    return {
        "total": total_count,
        "registrations_open": open_count
    }


@router.get("/sources")
async def get_hackathon_sources(db: AsyncSession = Depends(get_db_session)):
    """
    Get hackathon source counts grouped by platform.
    """
    
    # Get source counts
    query = select(Hackathon.source, func.count(Hackathon.id).label('count')).group_by(Hackathon.source)
    result = await db.execute(query)
    source_counts = result.all()
    
    return {
        source: count for source, count in source_counts
    }


@router.get("/locations")
async def get_hackathon_locations(db: AsyncSession = Depends(get_db_session)):
    """
    Get unique hackathon locations.
    """
    
    # Get distinct locations
    query = select(Hackathon.location).distinct().where(Hackathon.location.isnot(None))
    result = await db.execute(query)
    locations = [loc for (loc,) in result.all() if loc]
    
    # Sort locations - Online first, then alphabetically
    locations_sorted = sorted(locations, key=lambda x: (x.lower() != 'online', x.lower()))
    
    return {
        "locations": locations_sorted
    }


@router.get("/{hackathon_id}")
async def get_hackathon_details(
    hackathon_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get detailed information for a specific hackathon.
    """
    
    query = select(Hackathon).where(Hackathon.id == hackathon_id)
    result = await db.execute(query)
    hackathon = result.scalar_one_or_none()
    
    if not hackathon:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    
    return {
        "id": hackathon.id,
        "title": hackathon.title,
        "source": hackathon.source,
        "url": hackathon.url,
        "image_url": hackathon.image_url,
        "description": hackathon.description,
        "prize_pool": hackathon.prize_pool,
        "location": hackathon.location,
        "mode": hackathon.mode,
        "tags": json.loads(hackathon.tags) if hackathon.tags else [],
        "team_size_min": hackathon.team_size_min,
        "team_size_max": hackathon.team_size_max,
        "registration_deadline": hackathon.registration_deadline.isoformat() if hackathon.registration_deadline else None,
        "start_date": hackathon.start_date.isoformat() if hackathon.start_date else None,
        "end_date": hackathon.end_date.isoformat() if hackathon.end_date else None,
        "status": hackathon.status,
        "scraped_at": hackathon.scraped_at.isoformat() if hackathon.scraped_at else None
    }