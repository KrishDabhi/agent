# handler.py
import json
from typing import Any, Callable, Dict, List, Optional, Union, Tuple
from validator import validate_json, validate_request, JsonRpcError
from error import (
    METHOD_NOT_FOUND,
    INVALID_PARAMS,
    INTERNAL_ERROR,
    SERVER_ERROR
)

class JsonRpcHandler:
    
    def __init__(self):
        self._methods: Dict[str, Callable] = {}
    
    def register(self, method_name: str, handler: Callable) -> None:
        """Register a method handler (business logic lives HERE)"""
        if not callable(handler):
            raise TypeError("Handler must be callable")
        self._methods[method_name] = handler
    
    def handle(self, raw_data: str) -> Optional[str]:
        
        try:
            # Step 1: Parse raw JSON
            payload = validate_json(raw_data)
            
            # Step 2: Validate request structure
            validate_request(payload)
            
            # Step 3: Process request
            if isinstance(payload, list):
                return self._handle_batch(payload)
            return self._handle_single(payload)
        
        except JsonRpcError as e:
            return self._make_error_response(e.code, e.message, e.request_id)
        except Exception as e:
            # Fallback for unexpected errors
            return self._make_error_response(
                code=INTERNAL_ERROR,
                message=f"Internal error: {str(e)}",
                request_id=None
            )
    
    def _handle_single(self, req: Dict) -> Optional[str]:
        """Process single request per spec section 4.2"""
        is_notification = "id" not in req
        request_id = req.get("id")
        
        try:
            result = self._dispatch(req)
            
            # Notifications never get responses (even on success)
            if is_notification:
                return None
            
            return json.dumps({
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            })
        
        except JsonRpcError as e:
            # Notifications never get error responses
            if is_notification:
                return None
            
            return self._make_error_response(
                code=e.code,
                message=e.message,
                request_id=request_id
            )
        except Exception as e:
            if is_notification:
                return None
            return self._make_error_response(
                code=INTERNAL_ERROR,
                message=f"Internal error: {str(e)}",
                request_id=request_id
            )
    
    def _handle_batch(self, batch: List[Dict]) -> Optional[str]:
        """Process batch request per spec section 4.3"""
        responses = []
        
        for item in batch:
            # Skip notifications in batch processing
            if "id" not in item:
                try:
                    self._dispatch(item)
                except Exception:
                    # Notifications swallow all errors
                    pass
                continue
            
            try:
                result = self._dispatch(item)
                responses.append({
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": item["id"]
                })
            except JsonRpcError as e:
                responses.append({
                    "jsonrpc": "2.0",
                    "error": {"code": e.code, "message": e.message},
                    "id": item.get("id")
                })
            except Exception as e:
                responses.append({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": INTERNAL_ERROR,
                        "message": f"Internal error: {str(e)}"
                    },
                    "id": item.get("id")
                })
        
        return json.dumps(responses) if responses else None
    
    def _dispatch(self, req: Dict) -> Any:
        """Dispatch to registered method with params"""
        method_name = req["method"]
        
        if method_name not in self._methods:
            raise JsonRpcError(
                code=METHOD_NOT_FOUND,
                message=f"Method not found: '{method_name}'",
                request_id=req.get("id")
            )
        
        handler = self._methods[method_name]
        params = req.get("params", {})
        
        try:
            # Support both positional and named parameters
            if isinstance(params, list):
                return handler(*params)
            return handler(**params)
        except TypeError as e:
            raise JsonRpcError(
                code=INVALID_PARAMS,
                message=f"Invalid parameters: {str(e)}",
                request_id=req.get("id")
            )
        except Exception as e:
            # Convert application errors to standard format
            raise JsonRpcError(
                code=SERVER_ERROR,
                message=str(e),
                request_id=req.get("id")
            )
    
    @staticmethod
    def _make_error_response(code: int, message: str, request_id: Any) -> str:
        """Generate spec-compliant error response"""
        return json.dumps({
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id if request_id is not None else None
        })