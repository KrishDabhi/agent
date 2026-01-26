import json
from typing import Any, Union, List, Dict
from error import PARSE_ERROR, INVALID_REQUEST

class JsonRpcError(Exception):
    """Spec-compliant error container"""
    def __init__(self, code: int, message: str, request_id: Any = None):
        self.code = code
        self.message = message
        self.request_id = request_id
        super().__init__(f"[{code}] {message}")

def validate_json(raw_data: str) -> Union[Dict, List]:
    try:
        return json.loads(raw_data)
    except json.JSONDecodeError as e:
        raise JsonRpcError(
            code=PARSE_ERROR,
            message=f"Parse error: {str(e)}",
            request_id=None
        )

def validate_request(payload: Union[Dict, List]) -> None:
    if isinstance(payload, list):
        _validate_batch_request(payload)
    else:
        _validate_single_request(payload)

def _validate_batch_request(batch: List) -> None:
    if not batch:
        raise JsonRpcError(
            code=INVALID_REQUEST,
            message="Batch array cannot be empty",
            request_id=None
        )
    
    for item in batch:
        if not isinstance(item, dict):
            raise JsonRpcError(
                code=INVALID_REQUEST,
                message="Batch items must be objects",
                request_id=None
            )
        _validate_single_request(item)

def _validate_single_request(req: Dict) -> None:
    
    # Required fields
    if "jsonrpc" not in req or req["jsonrpc"] != "2.0":
        raise JsonRpcError(
            code=INVALID_REQUEST,
            message="Invalid jsonrpc version (must be '2.0')",
            request_id=req.get("id")
        )
    
    if "method" not in req or not isinstance(req["method"], str):
        raise JsonRpcError(
            code=INVALID_REQUEST,
            message="Missing/invalid 'method' field",
            request_id=req.get("id")
        )
    
    # Optional params validation
    if "params" in req and not isinstance(req["params"], (dict, list)):
        raise JsonRpcError(
            code=INVALID_REQUEST,
            message="'params' must be object or array",
            request_id=req.get("id")
        )
    
    # id validation (for calls)
    if "id" in req:
        if req["id"] is None:
            raise JsonRpcError(
                code=INVALID_REQUEST,
                message="'id' cannot be null",
                request_id=None
            )
        if not isinstance(req["id"], (str, int, float)):
            raise JsonRpcError(
                code=INVALID_REQUEST,
                message="'id' must be string, number, or null",
                request_id=req.get("id")
            )