from typing import Annotated

from fastapi import Depends

from .service import get_anon_ip

AnonIpDep = Annotated[str, Depends(get_anon_ip)]
