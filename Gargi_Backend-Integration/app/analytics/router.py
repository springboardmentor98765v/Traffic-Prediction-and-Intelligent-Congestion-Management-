import csv
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.analytics.heatmap_service import get_heatmap
from app.analytics.report_service import get_report_data
from app.analytics.schemas import TrendsResponse
from app.analytics.schemas_heatmap import HeatmapResponse
from app.analytics.schemas_reports import ReportResponse
from app.analytics.service import get_trends
from app.database.connection import get_db


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/trends",
    response_model=TrendsResponse,
)
def trends(
    road_id: int,
    range: str = "day",
    db: Session = Depends(get_db),
):
    try:
        return get_trends(
            db=db,
            road_id=road_id,
            range_name=range,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/heatmap",
    response_model=HeatmapResponse,
)
def heatmap(
    range: str = "day",
    db: Session = Depends(get_db),
):
    try:
        return get_heatmap(
            db=db,
            range_name=range,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get(
    "/reports",
)
def reports(
    range: str = "day",
    format: str = "json",
    db: Session = Depends(get_db),
):
    format = format.lower()

    if format not in {"json", "csv"}:
        raise HTTPException(
            status_code=400,
            detail="format must be json or csv",
        )

    try:
        data = get_report_data(
            db=db,
            range_name=range,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if format == "json":
        return {
            "range": range.lower(),
            "data": data,
        }

    output = io.StringIO()

    writer = csv.DictWriter(
        output,
        fieldnames=[
            "road_id",
            "timestamp",
            "vehicle_count",
            "density",
            "congestion_level",
        ],
    )

    writer.writeheader()
    writer.writerows(data)

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                f'attachment; filename="traffic_report_{range.lower()}.csv"'
            )
        },
    )
