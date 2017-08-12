from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from faker import Faker

from .models import CheckIn, School
from .forms import CheckInForm

fake = Faker()


@login_required
def home(request):
    """
    the homepage of the user
    """

    username = 'Aldo Raine'

    recent_checkins = [
        {
            'student': fake.name(),
            'teacher': fake.name(),
            'id': 1,
            'time': fake.date_time(),
        } for _ in range(8)
    ]

    context = {'username': username, 'recent_checkins': recent_checkins}
    return render(request, 'core/home.html', context=context)


def login(request):
    """
    used for logging in with an existing account
    """
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('/')


def signup(request):
    """
    used for signing up for the platform
    """
    return render(request, 'core/signup.html')


def forgotpassword(request):
    """
    view to enable sending password reset email
    """
    return render(request, 'core/forgotpassword.html')

@login_required
def profile(request):
    """
    displays user's info
    """

    context = {
        'name': f'{request.user.last_name}, {request.user.first_name}' if request.user.last_name else request.user.email,
        'avatar_url': request.user.avatar_url,
        'email': request.user.email,
        'schools': request.user.schools,
        'role': 'staff' if request.user.is_staff else 'user',
        'department': request.user.department,
        'recent_checkins': CheckIn.objects.order_by('created_on').all()[:10]
    }
    return render(request, 'core/profile.html', context)

@login_required
def profile_edit(request):
    """
    profile in editing state
    """
    context = {
        'name': f'{request.user.last_name}, {request.user.first_name}' if request.user.last_name else request.user.email,
        'avatar_url': request.user.avatar_url,
        'email': request.user.email,
        'schools': request.user.schools,
        'role': 'staff' if request.user.is_staff else 'user',
        'department': request.user.department,
        'recent_checkins': CheckIn.objects.order_by('created_on').all()[:10],
        'school_options': School.objects.filter(district=request.user.district).order_by('name').all()[:30]
    }
    return render(request, 'core/profile_edit.html', context)

@login_required
def checkins(request):
    """
    list all the checkins for teacher
    """

    if request.user.role=='DA':
        checkins = CheckIn.objects.filter(student__group=request.user.district)
    elif request.user.role=='SA':
        checkins = CheckIn.objects.filter(student__school=request.user.school)
    else:
        checkins = CheckIn.objects.filter(student__in=request.user.student_set.all())

    context = {'checkins': checkins.all()}
    return render(request, 'core/checkins.html', context)


@login_required
def checkins_add(request):
    """
    create a new checkin
    """

    if request.method == 'GET':
        form = CheckInForm(request.user)
    else:
        form = CheckInForm(request.user, request.POST)
        # If data is valid, proceeds to create a new CheckIn and redirect the user
        if form.is_valid():
            form.save()
            return redirect('checkins')

    return render(request, 'core/checkin_edit.html', {'form': form})

@login_required
def checkin(request, id):
    """
    view an individual checkin
    """
    checkin_event = get_object_or_404(CheckIn, pk=id)
    return render(request, 'core/checkin.html', {
        'checkin': checkin_event,
        'success_score_percentage': checkin_event.success_score / 10 * 100,
        }
    )

@login_required
def checkin_edit(request, id):
    """
    edit an individual checkin
    """

    checkin = get_object_or_404(CheckIn, pk=id)
    if request.method == 'GET':
        form = CheckInForm(request.user, instance=checkin)
    else:
        form = CheckInForm(request.user, request.POST, instance=checkin)
        if form.is_valid():
            form.save()
            return redirect('checkins')

    return render(request, 'core/checkin_edit.html', {'form': form})

@login_required
def teams(request):
    """
    Teacher: list of teams that the user is currently on
    Manager: list of all teams of the manager's group
    """
    return render(request, 'core/teams.html')

@login_required
def team(request, id):
    """
    view individual team
    """
    return render(request, 'core/team.html')


def privacy(request):
    """
    return the privacy policy
    """
    return render(request, 'core/privacy.html')
