from typing import Any, List, Optional, Union, Callable

import os
import sys

this_path = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.abspath(os.path.join(this_path, '..'))


def error_handling(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    e_str = f"{e}"
    try:
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        message = f"Filename: {fname}, line number: {exc_tb.tb_lineno}, type: {exc_type}. {e}"
    except Exception:
        message = e_str
    
    return message


def search_by_key(data: List[dict], key: str, value: Any) -> list[dict]:
    return [item for item in data if key in item and item[key] == value]
