from .start import router as start_router
from .modules import router as modules_router
from .goals import router as goals_router
from .admin import router as admin_router
from .menu import router as menu_router
from .help import router as help_router

all_routers = [
    start_router,
    menu_router,
    modules_router,
    goals_router,
    admin_router,
    help_router,
]