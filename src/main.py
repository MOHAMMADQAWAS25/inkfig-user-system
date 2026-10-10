from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.config.settings import get_settings
from src.interface.api.routes.administration import router as administration_router
from src.interface.api.routes.reports import router as reports_router
from src.interface.api.routes.authentication import router as authentication_router
from src.interface.api.routes.health import router as health_router
from src.interface.api.routes.password_reset import router as password_reset_router
from src.interface.api.routes.registration import router as registration_router
from src.interface.api.routes.settings import router as settings_router
from src.interface.api.routes.social_profiles import router as social_profiles_router
from src.interface.api.routes.notifications import router as notifications_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(registration_router, prefix=settings.api_prefix)
    app.include_router(authentication_router, prefix=settings.api_prefix)
    app.include_router(password_reset_router, prefix=settings.api_prefix)
    app.include_router(administration_router, prefix=settings.api_prefix)
    app.include_router(reports_router, prefix=settings.api_prefix)
    app.include_router(settings_router, prefix=settings.api_prefix)
    app.include_router(social_profiles_router, prefix=settings.api_prefix)
    app.include_router(notifications_router, prefix=settings.api_prefix)
    return app


app = create_app()
