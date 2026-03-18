from enum import Enum


class ListingCondition(str, Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    USED = "used"


class ListingStatus(str, Enum):
    ACTIVE = "active"
    SOLD = "sold"
    INACTIVE = "inactive"

