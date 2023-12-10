from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from myapp.models import RemoteCPUInfo
from django.contrib.auth.decorators import login_required


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class CustomLoginView(LoginView):
    template_name = "registration/login.html"


def admin_signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("admin_view")
    else:
        form = UserCreationForm()

    return render(request, "registration/admin_signup.html", {"form": form})


def admin_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("admin_view")
    else:
        form = AuthenticationForm()

    return render(request, "registration/admin_login.html", {"form": form})


@login_required
def admin_view(request):
    # Fetch the latest entry for each PC name
    pc_names = RemoteCPUInfo.objects.values("pc_name").distinct()

    # Create a dictionary to store PC name and status
    pc_dict = {}
    for pc_entry in pc_names:
        latest_entry = (
            RemoteCPUInfo.objects.filter(pc_name=pc_entry["pc_name"])
            .order_by("-timestamp")
            .first()
        )
        if latest_entry:
            pc_dict[pc_entry["pc_name"]] = latest_entry.status

    context = {"pc_dict": pc_dict}
    return render(request, "admin_view.html", context)


@login_required
def view_recent_details(request, pc_name):
    recent_details = (
        RemoteCPUInfo.objects.filter(pc_name=pc_name).order_by("-timestamp").first()
    )
    context = {"recent_details": recent_details}
    return render(request, "recent_details.html", context)

