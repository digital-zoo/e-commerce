from typing import Any, Dict, Optional, Union

import requests

IAMPORT_API_URL: str = ...
Amount = Union[int, float]

class Iamport(object):
    requests_session: requests.Session

    def __init__(self, imp_key: str, imp_secret: str, imp_url: str = ...) -> None: ...

    class ResponseError(Exception):
        code: Any
        message: Any
        def __init__(self, code: Optional[Any] = ..., message: Optional[Any] = ...) -> None: ...

    class HttpError(Exception):
        code: Any
        message: Any
        def __init__(self, code: Optional[Any] = ..., message: Optional[Any] = ...) -> None: ...

    @staticmethod
    def get_response(response: requests.Response) -> Dict: ...

    def _get_token(self) -> str: ...

    def get_headers(self) -> Dict[str, str]: ...

    def _get(self, url: str, payload: Optional[Dict[str, Any]] = ...) -> Dict: ...

    def _post(self, url: str, payload: Optional[Dict[str, Any]] = ...) -> Dict: ...

    def _delete(self, url: str) -> Dict: ...

    def find_by_status(self, status: str, **params) -> Dict: ...

    def find_by_merchant_uid(self, merchant_uid: str) -> Dict: ...

    def find_by_imp_uid(self, imp_uid: str) -> Dict: ...

    def find(self, **kwargs) -> Dict: ...

    def _cancel(self, payload: Dict[str, Any]) -> Dict: ...

    def pay_onetime(self, **kwargs) -> Dict: ...

    def pay_again(self, **kwargs) -> Dict: ...

    def customer_create(self, **kwargs) -> Dict: ...

    def customer_get(self, customer_uid: str) -> Dict: ...

    def customer_delete(self, customer_uid: str) -> Dict: ...

    def pay_foreign(self, **kwargs) -> Dict: ...

    def pay_schedule(self, **kwargs) -> Dict: ...

    def pay_schedule_get(self, merchant_id : str) -> Dict: ...

    def pay_schedule_get_between(self, **kwargs) -> Dict: ...

    def pay_unschedule(self, **kwargs) -> Dict: ...

    def cancel_by_merchant_uid(self, merchant_uid: str, reason: str, **kwargs) -> Dict: ...

    def cancel_by_imp_uid(self, imp_uid: str, reason: str, **kwargs) -> Dict: ...

    def cancel(self, reason: str, **kwargs) -> Dict: ...

    def is_paid(self, amount: Amount, **kwargs) -> bool: ...

    def prepare(self, merchant_uid: str, amount: Amount) -> Dict: ...

    def prepare_validate(self, merchant_uid: str, amount: Amount) -> Dict: ...

    def revoke_vbank_by_imp_uid(self, imp_uid: str) -> Dict: ...
    
    def certification_by_imp_uid(self, imp_uid: str) -> Dict: ...

    def find_certification(self, imp_uid: str) -> Dict: ...

    def cancel_certification(self, imp_uid: str) -> Dict: ...
