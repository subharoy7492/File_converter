from .stm_v3 import STMV3Engine
from .bijoy_v2 import BijoyV2Engine
from .bijoy_v1 import BijoyV1Engine
from .perfect_v4 import PerfectV4Engine
from .perfect_v5 import PerfectV5Engine
from .srv_v6 import TOPV6Engine
from .leap_v7 import LeapV7Engine

# Register all engine instances by their DISPLAY_NAME
CONVERTERS = {
    BijoyV1Engine.DISPLAY_NAME: BijoyV1Engine(),
    BijoyV2Engine.DISPLAY_NAME: BijoyV2Engine(),
    STMV3Engine.DISPLAY_NAME: STMV3Engine(),
    PerfectV4Engine.DISPLAY_NAME: PerfectV4Engine(),
    PerfectV5Engine.DISPLAY_NAME: PerfectV5Engine(),
    TOPV6Engine.DISPLAY_NAME: TOPV6Engine(),
    LeapV7Engine.DISPLAY_NAME: LeapV7Engine(),
}

def get_available_converters():
    """Returns a list of converter names for the frontend dropdown."""
    return list(CONVERTERS.keys())

def get_converter(name):
    """Retrieves an engine instance by display name, falling back to v1."""
    return CONVERTERS.get(name, CONVERTERS.get(BijoyV2Engine.DISPLAY_NAME))
