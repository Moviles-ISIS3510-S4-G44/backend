# Resumen de entidades y archivos del backend

Este documento consolida, en un solo lugar, las entidades actuales y los archivos relacionados (`models.py`, `schemas.py`, `service.py`, `routes.py`) para poder replicar la estructura en otro prompt.

## Routers registrados en la app principal

Archivo: `/home/runner/work/backend/backend/src/marketplace_andes_backend/app.py`

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .auth.routes import router as auth_router
from .categories.routes import router as categories_router
from .health.routes import router as health_router
from .interactions.routes import router as interactions_router
from .listings.routes import router as listings_router
from .users.routes import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(listings_router)
app.include_router(interactions_router)
```

---

## Entidad: User (módulo users)

### Rutas
- `GET /users`
- `GET /users/profile/{user_id}` (ruta anidada desde `users.profile`)

### Archivos
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/users/models.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/users/routes.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/users/profile/schemas.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/users/profile/service.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/users/profile/routes.py`

#### `users/models.py`
```python
from uuid import UUID, uuid7

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid7, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    rating: int = Field(default=0, ge=0, le=5)
```

#### `users/routes.py`
```python
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from src.marketplace_andes_backend.db import get_session
from .models import User
from .profile.routes import router as profile_router

router = APIRouter(prefix="/users", tags=["users"])
router.include_router(profile_router)


@router.get("", response_model=list[User])
def get_users(session: Session = Depends(get_session)) -> list[User]:
    statement = select(User)
    users = session.exec(statement).all()
    return users
```

#### `users/profile/schemas.py`
```python
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    rating: int = Field(ge=0, le=5)
```

#### `users/profile/service.py`
```python
from uuid import UUID

from sqlmodel import Session, select

from ..models import User


class UserProfileService:
    def __init__(self, session: Session):
        self.session = session

    def get_info(self, user_id: UUID) -> User | None:
        statement = select(User).where(User.id == user_id)
        return self.session.exec(statement).first()
```

#### `users/profile/routes.py`
```python
from uuid import UUID

from fastapi import APIRouter, HTTPException

from src.marketplace_andes_backend.auth.dependencies import CurrentUserDep
from src.marketplace_andes_backend.db import SessionDep

from .schemas import UserProfileResponse
from .service import UserProfileService

router = APIRouter(prefix="/profile", tags=["users"])


@router.get("/{user_id}")
async def get_user_profile(
    user_id: UUID,
    _current_user: CurrentUserDep,
    session: SessionDep,
) -> UserProfileResponse:
    service = UserProfileService(session)
    user = service.get_info(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfileResponse.model_validate(user)
```

---

## Entidad: UserAuth (módulo auth)

### Rutas
- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`

### Archivos
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/auth/models.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/auth/schemas.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/auth/service.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/auth/routes.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/auth/dependencies.py`

#### `auth/models.py`
```python
from uuid import UUID

from sqlalchemy import CheckConstraint
from sqlmodel import Field, SQLModel


class UserAuth(SQLModel, table=True):
    __tablename__ = "user_auth"
    __table_args__ = (CheckConstraint("id = user_id", name="ck_user_auth_id_matches_user_id"),)

    id: UUID = Field(primary_key=True, foreign_key="user.id")
    user_id: UUID = Field(foreign_key="user.id", index=True, unique=True)
    hashed_password: str
```

#### `auth/schemas.py`
```python
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SignupRequest(BaseModel):
    name: str = Field(min_length=1)
    email: str = Field(min_length=1)
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    rating: int = Field(ge=0, le=5)
```

#### `auth/service.py`
```python
from datetime import UTC, datetime, timedelta
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError as JWTInvalidTokenError
from sqlmodel import Session, select

from ..config import get_settings
from ..users.models import User
from .models import UserAuth

PWD_HASHER = PasswordHasher()


class DuplicateEmailError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.settings = get_settings()

    def hash_password(self, password: str) -> str:
        return PWD_HASHER.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        try:
            return PWD_HASHER.verify(hashed_password, password)
        except (InvalidHashError, VerificationError):
            return False

    def create_access_token(self, user: User) -> str:
        expires_at = datetime.now(UTC) + timedelta(
            minutes=self.settings.jwt_access_token_expire_minutes
        )
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "exp": expires_at,
        }
        return jwt.encode(
            payload,
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm,
        )

    def decode_access_token(self, token: str) -> dict[str, str]:
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm],
            )
        except (ExpiredSignatureError, JWTInvalidTokenError) as exc:
            raise InvalidTokenError() from exc

        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise InvalidTokenError()

        return payload

    def signup(self, name: str, email: str, password: str) -> User:
        existing_user = self.session.exec(select(User).where(User.email == email)).first()
        if existing_user is not None:
            raise DuplicateEmailError()

        user = User(name=name, email=email)
        self.session.add(user)
        self.session.flush()
        if user.id is None:
            raise InvalidTokenError()

        user_auth = UserAuth(
            id=user.id,
            user_id=user.id,
            hashed_password=self.hash_password(password),
        )
        self.session.add(user_auth)
        self.session.commit()
        self.session.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> str:
        user = self.session.exec(select(User).where(User.email == email)).first()
        if user is None:
            raise InvalidCredentialsError()

        user_auth = self.session.exec(
            select(UserAuth).where(UserAuth.user_id == user.id)
        ).first()
        if user_auth is None or not self.verify_password(password, user_auth.hashed_password):
            raise InvalidCredentialsError()

        return self.create_access_token(user)

    def get_user_by_token(self, token: str) -> User:
        payload = self.decode_access_token(token)
        try:
            user_id = UUID(payload["sub"])
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidTokenError() from exc

        user = self.session.exec(select(User).where(User.id == user_id)).first()
        if user is None:
            raise InvalidTokenError()

        return user
```

#### `auth/routes.py`
```python
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .dependencies import AuthServiceDep, CurrentUserDep
from .schemas import CurrentUserResponse, SignupRequest, TokenResponse
from .service import DuplicateEmailError, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, auth_service: AuthServiceDep) -> CurrentUserResponse:
    try:
        user = auth_service.signup(
            name=payload.name,
            email=payload.email,
            password=payload.password,
        )
    except DuplicateEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from exc

    return CurrentUserResponse.model_validate(user)


@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
) -> TokenResponse:
    try:
        access_token = auth_service.authenticate(
            email=form_data.username,
            password=form_data.password,
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get("/me")
def read_current_user(current_user: CurrentUserDep) -> CurrentUserResponse:
    return CurrentUserResponse.model_validate(current_user)
```

#### `auth/dependencies.py`
```python
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ..db import SessionDep
from ..users.models import User
from .service import AuthService, InvalidTokenError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthServiceDep,
) -> User:
    try:
        return auth_service.get_user_by_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


CurrentUserDep = Annotated[User, Depends(get_current_user)]
```

---

## Entidad: Category (módulo categories)

### Rutas
- `POST /categories`
- `GET /categories`
- `GET /categories/{category_id}`

### Archivos
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/categories/models.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/categories/schemas.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/categories/service.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/categories/routes.py`

#### `categories/models.py`
```python
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
```

#### `categories/schemas.py`
```python
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CategoryCreateRequest(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
```

#### `categories/service.py`
```python
from sqlmodel import Session, select

from .models import Category


class CategoryService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, payload: Category) -> Category:
        self.session.add(payload)
        self.session.commit()
        self.session.refresh(payload)
        return payload

    def list_all(self) -> list[Category]:
        statement = select(Category)
        return list(self.session.exec(statement).all())

    def get_by_id(self, category_id: int) -> Category | None:
        statement = select(Category).where(Category.id == category_id)
        return self.session.exec(statement).first()
```

#### `categories/routes.py`
```python
from fastapi import APIRouter, HTTPException

from src.marketplace_andes_backend.db import SessionDep

from .models import Category
from .schemas import CategoryCreateRequest, CategoryResponse
from .service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("")
async def create_category(
    payload: CategoryCreateRequest,
    session: SessionDep,
) -> CategoryResponse:
    service = CategoryService(session)
    category = service.create(Category(name=payload.name))
    return CategoryResponse.model_validate(category)


@router.get("")
async def list_categories(session: SessionDep) -> list[CategoryResponse]:
    service = CategoryService(session)
    categories = service.list_all()
    return [CategoryResponse.model_validate(category) for category in categories]


@router.get("/{category_id}")
async def get_category(
    category_id: int,
    session: SessionDep,
) -> CategoryResponse:
    service = CategoryService(session)
    category = service.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse.model_validate(category)
```

---

## Entidad: Listing (módulo listings)

### Rutas
- `POST /listings`
- `GET /listings`
- `GET /listings/{listing_id}`

### Archivos
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/listings/models.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/listings/schemas.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/listings/service.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/listings/routes.py`

#### `listings/models.py`
```python
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Listing(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    seller_id: UUID = Field(foreign_key="user.id")
    category_id: UUID = Field(foreign_key="category.id")
    title: str
    description: str
    price: Decimal
    condition: str
    images: list[str] = Field(sa_column=Column(JSONB))
    status: str
    location: str
```

#### `listings/schemas.py`
```python
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ListingCreateRequest(BaseModel):
    seller_id: UUID
    category_id: UUID
    title: str
    description: str
    price: Decimal
    condition: str
    images: list[str]
    status: str
    location: str


class ListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    seller_id: UUID
    category_id: UUID
    title: str
    description: str
    price: Decimal
    condition: str
    images: list[str]
    status: str
    location: str
```

#### `listings/service.py`
```python
from uuid import UUID

from sqlmodel import Session, select

from src.marketplace_andes_backend.categories.models import Category
from src.marketplace_andes_backend.users.models import User

from .models import Listing


class ListingService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, payload: Listing) -> Listing:
        self.session.add(payload)
        self.session.commit()
        self.session.refresh(payload)
        return payload

    def list_all(self) -> list[Listing]:
        statement = select(Listing)
        return list(self.session.exec(statement).all())

    def get_by_id(self, listing_id: UUID) -> Listing | None:
        statement = select(Listing).where(Listing.id == listing_id)
        return self.session.exec(statement).first()

    def user_exists(self, user_id: UUID) -> bool:
        statement = select(User).where(User.id == user_id)
        return self.session.exec(statement).first() is not None

    def category_exists(self, category_id: UUID) -> bool:
        statement = select(Category).where(Category.id == category_id)
        return self.session.exec(statement).first() is not None
```

#### `listings/routes.py`
```python
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path

from src.marketplace_andes_backend.db import SessionDep

from .models import Listing
from .schemas import ListingCreateRequest, ListingResponse
from .service import ListingService

router = APIRouter(prefix="/listings", tags=["listings"])


@router.post("")
async def create_listing(
    payload: ListingCreateRequest,
    session: SessionDep,
) -> ListingResponse:
    service = ListingService(session)
    if not service.user_exists(payload.seller_id):
        raise HTTPException(status_code=404, detail="Seller not found")
    if not service.category_exists(payload.category_id):
        raise HTTPException(status_code=404, detail="Category not found")

    listing = service.create(Listing(**payload.model_dump()))
    return ListingResponse.model_validate(listing)


@router.get("")
async def list_listings(session: SessionDep) -> list[ListingResponse]:
    service = ListingService(session)
    listings = service.list_all()
    return [ListingResponse.model_validate(listing) for listing in listings]


@router.get("/{listing_id}")
async def get_listing(
    listing_id: Annotated[UUID, Path()],
    session: SessionDep,
) -> ListingResponse:
    service = ListingService(session)
    listing = service.get_by_id(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return ListingResponse.model_validate(listing)
```

---

## Entidad: UserListingInteraction (módulo interactions)

### Rutas
- `POST /interactions`
- `GET /interactions/users/{user_id}/top`

### Archivos
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/interactions/models.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/interactions/schemas.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/interactions/service.py`
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/interactions/routes.py`

#### `interactions/models.py`
```python
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class UserListingInteraction(SQLModel, table=True):
    __tablename__ = "user_listing_interaction"
    __table_args__ = (
        UniqueConstraint("user_id", "listing_id", name="uq_user_listing_interaction"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    listing_id: UUID = Field(foreign_key="listing.id")
    interaction_count: int = Field(default=1, ge=1)
    last_interaction_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
```

#### `interactions/schemas.py`
```python
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InteractionRegisterRequest(BaseModel):
    user_id: UUID
    listing_id: UUID


class InteractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    listing_id: UUID
    interaction_count: int
    last_interaction_at: datetime
```

#### `interactions/service.py`
```python
from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Session, desc, select

from src.marketplace_andes_backend.listings.models import Listing
from src.marketplace_andes_backend.users.models import User

from .models import UserListingInteraction


class InteractionService:
    def __init__(self, session: Session):
        self.session = session

    def user_exists(self, user_id: UUID) -> bool:
        statement = select(User).where(User.id == user_id)
        return self.session.exec(statement).first() is not None

    def listing_exists(self, listing_id: UUID) -> bool:
        statement = select(Listing).where(Listing.id == listing_id)
        return self.session.exec(statement).first() is not None

    def get_by_user_and_listing(
        self, user_id: UUID, listing_id: UUID
    ) -> UserListingInteraction | None:
        statement = select(UserListingInteraction).where(
            UserListingInteraction.user_id == user_id,
            UserListingInteraction.listing_id == listing_id,
        )
        return self.session.exec(statement).first()

    def register_interaction(self, user_id: UUID, listing_id: UUID) -> UserListingInteraction:
        interaction = self.get_by_user_and_listing(user_id=user_id, listing_id=listing_id)

        if interaction:
            interaction.interaction_count += 1
            interaction.last_interaction_at = datetime.now(timezone.utc)
            self.session.add(interaction)
        else:
            interaction = UserListingInteraction(
                user_id=user_id,
                listing_id=listing_id,
                interaction_count=1,
                last_interaction_at=datetime.now(timezone.utc),
            )
            self.session.add(interaction)

        self.session.commit()
        self.session.refresh(interaction)
        return interaction

    def get_top_interactions_by_user(self, user_id: UUID) -> list[UserListingInteraction]:
        statement = (
            select(UserListingInteraction)
            .where(UserListingInteraction.user_id == user_id)
            .order_by(desc(UserListingInteraction.interaction_count))
            .limit(4)
        )
        return list(self.session.exec(statement).all())
```

#### `interactions/routes.py`
```python
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path

from src.marketplace_andes_backend.db import SessionDep

from .schemas import InteractionRegisterRequest, InteractionResponse
from .service import InteractionService

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("")
async def register_interaction(
    payload: InteractionRegisterRequest,
    session: SessionDep,
) -> InteractionResponse:
    service = InteractionService(session)

    if not service.user_exists(payload.user_id):
        raise HTTPException(status_code=404, detail="User not found")

    if not service.listing_exists(payload.listing_id):
        raise HTTPException(status_code=404, detail="Listing not found")

    interaction = service.register_interaction(
        user_id=payload.user_id,
        listing_id=payload.listing_id,
    )
    return InteractionResponse.model_validate(interaction)


@router.get("/users/{user_id}/top")
async def get_top_user_interactions(
    user_id: Annotated[UUID, Path()],
    session: SessionDep,
) -> list[InteractionResponse]:
    service = InteractionService(session)

    if not service.user_exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    interactions = service.get_top_interactions_by_user(user_id)
    return [InteractionResponse.model_validate(item) for item in interactions]
```

---

## Módulo adicional: health (solo rutas)

### Ruta
- `GET /health`

### Archivo
- `/home/runner/work/backend/backend/src/marketplace_andes_backend/health/routes.py`

```python
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    return {"status": "healthy", "service": "backend"}
```

