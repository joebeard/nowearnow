class PrivacyHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/admin/"):
            # Django form CSRF checks need an origin on native form submissions.
            # Public scan/API responses retain no-referrer.
            response["Referrer-Policy"] = "same-origin"
        response["Cache-Control"] = "no-store"
        response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response
