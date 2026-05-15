from app.db.declarative import Base


# Import models here for Alembic
from app.models.user import User  # noqa: E402
from app.models.property import Property, PropertyImage  # noqa: E402
from app.models.visit_request import VisitRequest  # noqa: E402
from app.models.notification import Notification  # noqa: E402
