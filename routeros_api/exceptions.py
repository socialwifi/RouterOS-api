class RouterOsApiError(Exception):
    pass

class RouterOsApiConnectionError(RouterOsApiError):
    pass

class FatalRouterOsApiError(RouterOsApiError):
    pass

class RouterOsApiParsingError(RouterOsApiError):
    pass
