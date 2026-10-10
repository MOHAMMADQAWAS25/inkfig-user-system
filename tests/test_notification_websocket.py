from pathlib import Path

from fastapi.routing import APIRoute

from src.main import create_app

ROOT = Path(__file__).resolve().parents[1]


def test_websocket_notification_contract_and_infrastructure() -> None:
    routes = {
        route.path: route.methods or set()
        for route in create_app().routes
        if isinstance(route, APIRoute)
    }
    assert "POST" in routes["/api/v1/notifications/socket-ticket"]
    migration = (
        ROOT / "migrations" / "20261008_016_create_websocket_connections.sql"
    ).read_text()
    template = (ROOT / "template.yaml").read_text()
    handler = (ROOT / "src" / "websocket_handler.py").read_text()
    realtime = (
        ROOT / "src" / "infrastructure" / "integrations" / "notification_realtime.py"
    ).read_text()
    reports = (ROOT / "src" / "interface" / "api" / "routes" / "reports.py").read_text()
    assert "websocket_connections" in migration
    assert "NotificationWebSocketApi" in template
    assert "$connect" in template and "$disconnect" in template
    assert 'claims.get("type") != "websocket"' in handler
    assert 'RolePermissionModel.permission_code == "reports.manage"' in realtime
    assert '"reports.changed"' in realtime
    assert "publish_reports_changed(session)" in reports
