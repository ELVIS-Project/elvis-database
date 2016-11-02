from elvis.views.main import TOSPage


class ElvisTermsOfServiceMiddleware:
    # A set of paths prefixes that don't need to be protected by TOS.
    UNPROTECTED_PATHS = {'/logout'}

    def process_view(self, request, view_func, view_args, view_kwarg):
        user = request.user
        if self._should_redirect(request, user):
            final_view = TOSPage.as_view()
        else:
            final_view = view_func
        return final_view(request, *view_args, **view_kwarg)

    def _should_redirect(self, request, user):
        """Figure out if user should be redirected to TOS screen."""
        if request.method != "GET" or user.is_anonymous() or \
                any(request.path.startswith(p) for p in self.UNPROTECTED_PATHS):
            return False

        # Use the session to store a bool concerning TOS acceptance.
        # Avoid doing a DB lookup on every request.
        accepted_tos = request.session.get("ACCEPTED_TOS")
        if accepted_tos is None:
            accepted_tos = user.userprofile.accepted_tos
            request.session['ACCEPTED_TOS'] = accepted_tos

        if accepted_tos:
            return False
        else:
            return True


