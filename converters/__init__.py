from .bijoy_v1 import BijoyToUnicodeV1
from .stm_v3 import StmToUnicodeV3
from .srv_v6 import SrvToUnicodeV6

CONVERTERS = {
    'bijoy_v1': {
        'name': 'Bijoy Engine v1.0 (Standard)',
        'instance': BijoyToUnicodeV1()
    },
    'stm_v3': {
        'name': 'STM Engine v3.0 (Advanced)',
        'instance': StmToUnicodeV3()
    },
    'srv_v6': {
        'name': 'SRV Engine v6.0 (Advanced)',
        'instance': SrvToUnicodeV6()
    }
}

def get_converter(version_key):
    converter_info = CONVERTERS.get(version_key)
    if not converter_info:
        raise ValueError(f"Converter version '{version_key}' is not available.")
    return converter_info['instance']
