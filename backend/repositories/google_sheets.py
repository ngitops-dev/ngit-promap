from typing import Any

from backend.config import settings
from backend.services.google_auth import get_sheets_service
from backend.utils.logging import get_logger

logger = get_logger(__name__)


def _sheet_service():
    return get_sheets_service()


def read_sheet(tab_name: str) -> list[dict[str, Any]]:
    service = _sheet_service()
    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=settings.GOOGLE_SHEET_ID,
            range=f"{tab_name}!A:Z",
        )
        .execute()
    )
    values = result.get("values", [])
    if len(values) < 2:
        return []
    headers = [h.strip() for h in values[0]]
    rows = []
    for row in values[1:]:
        padded = row + [""] * (len(headers) - len(row))
        rows.append(dict(zip(headers, padded[: len(headers)])))
    return rows


def find_row(tab_name: str, column: str, value: str) -> dict[str, Any] | None:
    rows = read_sheet(tab_name)
    for row in rows:
        if row.get(column, "").strip() == value.strip():
            return row
    return None


def find_rows(tab_name: str, column: str, value: str) -> list[dict[str, Any]]:
    rows = read_sheet(tab_name)
    return [row for row in rows if row.get(column, "").strip() == value.strip()]


def find_rows_by_multi(
    tab_name: str, filters: dict[str, str]
) -> list[dict[str, Any]]:
    rows = read_sheet(tab_name)
    results = []
    for row in rows:
        match = all(
            row.get(col, "").strip() == val.strip() for col, val in filters.items()
        )
        if match:
            results.append(row)
    return results


def append_row(tab_name: str, data: dict[str, Any]) -> None:
    service = _sheet_service()
    existing = read_sheet(tab_name)
    if existing:
        headers = list(existing[0].keys())
    else:
        headers = list(data.keys())
    row = [data.get(h, "") for h in headers]
    service.spreadsheets().values().append(
        spreadsheetId=settings.GOOGLE_SHEET_ID,
        range=f"{tab_name}!A:A",
        valueInputOption="USER_ENTERED",
        body={"values": [row]},
    ).execute()
    logger.info("Appended row to %s", tab_name)


def update_row(
    tab_name: str, column: str, value: str, data: dict[str, Any]
) -> bool:
    service = _sheet_service()
    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=settings.GOOGLE_SHEET_ID,
            range=f"{tab_name}!A:Z",
        )
        .execute()
    )
    values = result.get("values", [])
    if len(values) < 2:
        return False
    headers = [h.strip() for h in values[0]]
    target_col_idx = headers.index(column) if column in headers else -1
    if target_col_idx == -1:
        return False
    for i, row in enumerate(values[1:], start=2):
        padded = row + [""] * (len(headers) - len(row))
        if padded[target_col_idx].strip() == value.strip():
            for key, val in data.items():
                if key in headers:
                    col_idx = headers.index(key)
                    while len(row) <= col_idx:
                        row.append("")
                    row[col_idx] = str(val)
            update_range = f"{tab_name}!A{i}:Z{i}"
            service.spreadsheets().values().update(
                spreadsheetId=settings.GOOGLE_SHEET_ID,
                range=update_range,
                valueInputOption="USER_ENTERED",
                body={"values": [row]},
            ).execute()
            logger.info("Updated row in %s where %s=%s", tab_name, column, value)
            return True
    return False


def get_next_id(tab_name: str, id_column: str, prefix: str) -> str:
    rows = read_sheet(tab_name)
    max_num = 0
    for row in rows:
        existing_id = row.get(id_column, "")
        if existing_id.startswith(prefix):
            try:
                num = int(existing_id[len(prefix) :])
                max_num = max(max_num, num)
            except ValueError:
                continue
    return f"{prefix}{max_num + 1:04d}"
