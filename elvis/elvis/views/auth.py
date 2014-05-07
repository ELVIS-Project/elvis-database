from django.contrib.auth.views import logout
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.contrib.auth.forms import AuthenticationForm


class LoginFormView(View):
    form_class = AuthenticationForm
    template_name = 'login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("/")
        else:
            return render(request, self.template_name, {'form': form})

def logout_view(request):
    """
    Logs out the current user.
    """
    logout(request)
    next = request.GET.get('next', None)
    if next:
        return redirect(next)
    else:
        return redirect('/')