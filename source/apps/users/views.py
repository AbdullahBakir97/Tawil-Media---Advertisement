from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetConfirmView as DjangoPasswordResetConfirmView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import FormView, TemplateView

from .forms import LoginForm, PasswordResetForm, ProfileForm, RegisterForm, SetPasswordForm


def _hx_redirect(request, url):
    """Redirect that works for both normal and HTMX requests."""
    if request.headers.get("HX-Request"):
        response = HttpResponse(status=204)
        response["HX-Redirect"] = url
        return response
    return HttpResponseRedirect(url)


class LoginView(FormView):
    template_name = "auth/login.html"
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("profile")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        login(self.request, form.user)
        if not form.cleaned_data.get("remember"):
            self.request.session.set_expiry(0)
        next_url = self.request.POST.get("next") or self.request.GET.get("next") or reverse("profile")
        return _hx_redirect(self.request, next_url)


class RegisterView(FormView):
    template_name = "auth/register.html"
    form_class = RegisterForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, _("Welcome to Tawil Media, %(name)s!") % {"name": user.first_name})
        return _hx_redirect(self.request, reverse("profile"))


@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")


class PasswordResetView(FormView):
    template_name = "auth/password/reset.html"
    form_class = PasswordResetForm

    def form_valid(self, form):
        form.save(
            request=self.request,
            use_https=self.request.is_secure(),
            email_template_name="auth/password/reset_email.txt",
            subject_template_name="auth/password/reset_subject.txt",
        )
        messages.info(self.request, _("If an account exists for that address, a reset link has been sent."))
        return _hx_redirect(self.request, reverse("login"))


class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    template_name = "auth/password/change.html"
    form_class = SetPasswordForm
    success_url = reverse_lazy("login")
    post_reset_login = True

    def form_valid(self, form):
        messages.success(self.request, _("Your password has been changed. You are now signed in."))
        super().form_valid(form)
        return _hx_redirect(self.request, str(self.get_success_url()))


class PasswordChangeView(LoginRequiredMixin, FormView):
    template_name = "auth/password/change.html"
    form_class = SetPasswordForm
    success_url = reverse_lazy("profile")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        login(self.request, self.request.user)  # keep the session valid after the hash changes
        messages.success(self.request, _("Your password has been changed."))
        return _hx_redirect(self.request, str(self.success_url))


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "auth/profile/dashboard.html"


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "auth/profile/settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("profile_form", ProfileForm(instance=self.request.user))
        return context


@method_decorator(login_required, name="dispatch")
class UpdateProfileView(View):
    """HTMX target for the profile section of the settings page."""

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profile updated."))
            return _hx_redirect(request, reverse("settings"))
        return render(request, "auth/profile/settings.html", {"profile_form": form})


@method_decorator(login_required, name="dispatch")
class UpdateSecurityView(View):
    def post(self, request):
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            login(request, request.user)
            messages.success(request, _("Password updated."))
            return _hx_redirect(request, reverse("settings"))
        return render(request, "auth/profile/settings.html", {"security_form": form})


@method_decorator(login_required, name="dispatch")
class UpdateNotificationsView(View):
    """Notification preferences are not persisted yet; acknowledge the request."""

    def post(self, request):
        messages.info(request, _("Notification preferences will be available soon."))
        return _hx_redirect(request, reverse("settings"))
