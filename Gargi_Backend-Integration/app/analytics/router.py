import csv
import io
from datetime import date

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
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    if road_id == 4:
        raise HTTPException(
            status_code=404,
            detail="Road 4 is not available.",
        )

    try:
        return get_trends(
            db=db,
            road_id=road_id,
            range_name=range,
            start_date=start_date,
            end_date=end_date,
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
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    try:
        return get_heatmap(
            db=db,
            range_name=range,
            start_date=start_date,
            end_date=end_date,
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
    start_date: date | None = None,
    end_date: date | None = None,
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
            start_date=start_date,
            end_date=end_date,
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

from fastapi import HTTPException

from app.analytics.intelligence_service import (
    build_recommendations,
    evaluate_model,
)


@router.get("/model-evaluation")
def model_evaluation(
    road_id: int,
    db: Session = Depends(get_db),
):
    if road_id == 4:
        raise HTTPException(status_code=404, detail="Road 4 is not available.")

    result = evaluate_model(db=db, road_id=road_id)
    return result


@router.get("/recommendations")
def recommendations(
    road_id: int = 1,
    db: Session = Depends(get_db),
):
    if road_id == 4:
        raise HTTPException(status_code=404, detail="Road 4 is not available.")

    try:
        return build_recommendations(db=db, road_id=road_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
