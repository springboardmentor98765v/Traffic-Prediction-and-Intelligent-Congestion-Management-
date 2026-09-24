from typing import Optional, Union
from fastapi import APIRouter, Query, Response, HTTPException, status
from fastapi.responses import PlainTextResponse

from app.schemas.analytics import TrafficTrendResponse, HeatmapResponse, HistoricalReportSummary
from app.services import analytics_service
from app.services.traffic_service import ROAD_NAMES

router = APIRouter()


@router.get(
    "/trends",
    response_model=TrafficTrendResponse,
    summary="Traffic Trend Analysis (FR-05)",
    description=(
        "Retrieve traffic trend patterns for a specific road over daily or weekly timeframes. "
        "Returns average congestion scores and traffic KPIs per time bucket."
    )
)
def get_traffic_trends(
    road_id: str = Query(..., description="Road identifier, e.g. R001"),
    range: str = Query("day", pattern="^(day|week)$", description="Aggregation timeframe: day or week")
):
    normalized_id = road_id.strip().upper()
    if normalized_id not in ROAD_NAMES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Road '{road_id}' not found. Available roads: {list(ROAD_NAMES.keys())}"
        )

    return analytics_service.get_traffic_trends(road_id=normalized_id, range_type=range)


@router.get(
    "/heatmap",
    response_model=HeatmapResponse,
    summary="Congestion Heatmap Matrix (FR-06)",
    description=(
        "Retrieve aggregated congestion intensity across all monitored roads and time buckets. "
        "Provides 2D matrix structure optimized for UI heatmap rendering."
    )
)
def get_congestion_heatmap(
    range: str = Query("day", pattern="^(day|week)$", description="Aggregation timeframe: day or week")
):
    return analytics_service.get_congestion_heatmap(range_type=range)


@router.get(
    "/reports",
    summary="Downloadable Historical Reports (FR-07)",
    description=(
        "Generate and download historical traffic reports. "
        "Supports CSV format for spreadsheet export and JSON format for dashboard reporting."
    )
)
def get_historical_reports(
    range: str = Query("week", description="Report timeframe: day, week, or month"),
    format: str = Query("csv", pattern="^(csv|json)$", description="Output format: csv or json")
):
    data = analytics_service.generate_historical_report(range_type=range, format_type=format)

    if format.lower() == "csv":
        return Response(
            content=data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=traffic_report_{range}.csv"
            }
        )

    return data
