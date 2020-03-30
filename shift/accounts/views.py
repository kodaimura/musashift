from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from .forms import LoginForm, ProfileForm, DaysForm
from .models import Profile


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'accounts/login.html'

class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'accounts/login.html'

    
def signup(request):
    user_form = UserCreationForm(request.POST)
    profile_form = ProfileForm(request.POST)  #{{ form.as_p }}の部分で表示される
    if request.method == 'POST' and user_form.is_valid() and profile_form.is_valid():
            
        user = user_form.save(commit=False)
        user.is_active = True
        user.save()
        
        profile = profile_form.save(commit=False)
        profile.user = user
        profile.save()
        return redirect('../login/')
        
    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }
        
    return render(request, 'accounts/signup.html', context)
    
    

def days_choice(request):
    days = ""
    days_late = ""

    state = Profile.objects.get(id=request.user.id).days
    state_late = Profile.objects.get(id=request.user.id).days_late

    form = DaysForm(request.POST or None,initial={'days': state, 'days_late':state_late})
    
    if request.method == 'POST' and form.is_valid():
        obj = Profile.objects.get(id=request.user.id)
        form = DaysForm(request.POST, instance = obj)
        
        form.save(commit = False)
        
        days = "定刻出勤可を"+str(form.cleaned_data['days'])+"日に変更"
        days_late = "遅れ出勤可を"+str(form.cleaned_data['days_late'])+"日に変更"
        
        
        if not (dayscheck(form.cleaned_data['days'],form.cleaned_data['days_late'])):
            days = "登録できませんでした。"
            days_late = "形式の間違い、または日付の重複があります。"
                        
        else:
            if form.cleaned_data['days'] == None:
                form.days = state
                days = ""
                
            if form.cleaned_data['days_late'] == None:
                form.days_late = state_late
                days_late = ""
    
            form.save()
                
    state = ""
    state_late = ""
    
    if not request.user.profile.days in [None, '0']:
        state = request.user.profile.days
    if not request.user.profile.days in [None, '0']:
        state_late = request.user.profile.days_late
    
    params = {
        'form': form,
        'name': request.user.profile.name,
        'days': days,
        'days_late': days_late,
        'state': state,
        'state_late': state_late,

    }
    return render(request, 'accounts/dayschoice.html', params)
        


def dayscheck(days, days_late):
    notls = []
    d1 = 0
    d10 = 0
    if days == None and days_late == None:
        return True
    
    if days == None:
        pass
    else:
        for day in days:
            if d10 != 0 and day.isdecimal() and day.isalnum():
                return False
            elif day.isdecimal() and day.isalnum():
                if int(d1) == 0:
                    d1 = int(day)
                else:
                    d10 = d1
                    d1 = int(day)
            elif day == '.' or day == ',':
                if d10 * 10 + d1 > 31:
                    return False
                if d10 * 10 + d1 in notls:
                    return False
                notls.append(d10 * 10 + d1)
                d1 = 0
                d10 = 0
            else:
                return False
        if d10 * 10 + d1 > 31:
            return False
        elif d10 * 10 + d1 != 0:
            if d10 * 10 + d1 in notls:
                return False
            notls.append(d10 * 10 + d1)
            d1 = 0
            d10 = 0
        
    if days_late == None:
        pass
    else:
        for day in days_late:
            if d10 != 0 and day.isdecimal() and day.isalnum():
                return False
            elif day.isdecimal() and day.isalnum():
                if int(d1) == 0:
                    d1 = int(day)
                else:
                    d10 = d1
                    d1 = int(day)
            elif day == '.' or day == ',':
                if d10 * 10 + d1 > 31:
                    return False
                if d10 * 10 + d1 in notls:
                    return False
                notls.append(d10 * 10 + d1)
                d1 = 0
                d10 = 0
            else:
                return False
        if d10 * 10 + d1 > 31:
            return False
        elif d10 * 10 + d1 != 0:
            if d10 * 10 + d1 in notls:
                return False

    return True
            
            
