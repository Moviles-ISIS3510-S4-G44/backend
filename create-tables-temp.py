from sqlmodel import SQLModel

import marketplace_andes_backend.users.models
import marketplace_andes_backend.categories.models
import marketplace_andes_backend.listings.models
from marketplace_andes_backend.db import get_engine

SQLModel.metadata.create_all(get_engine())
print("Tablas creadas.")