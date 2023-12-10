class RemoteAddrMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        x_real_ip = request.META.get("HTTP_X_REAL_IP")
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if x_real_ip:
            request.META["REMOTE_ADDR"] = x_real_ip
        elif x_forwarded_for:
            request.META["REMOTE_ADDR"] = x_forwarded_for.split(",")[0]

        return self.get_response(request)
