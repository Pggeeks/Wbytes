from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth import authenticate, login
from .forms.user_form import ChangePasswordForm, CustomUserCreationForm, LoginForm
import re
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout

class RegisterView(View):
    form_class = CustomUserCreationForm
    template_name = 'users/signup.html'

    def dispatch(self, request, *args, **kwargs):
        ## Redirect user too dashbooard if he tries to go to signup page
        if request.user.is_authenticated:
            return redirect(to='/dashboard')
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('login')
        return render(request, self.template_name, {'form': form})

class CustomLoginView(View):
    template_name = 'users/login.html'
    form_class = LoginForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email_or_username = form.cleaned_data['email_or_username']
            password = form.cleaned_data['password']
            ## As user is inputing email and username in same field, we are using regex to check
            ##- is it usernname or email and validating accordingly
            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email_or_username):
                kwargs = {'email': email_or_username}
            elif re.match(r'^[\w.@+-]+$', email_or_username):
                kwargs = {'username': email_or_username}
            else:
                messages.error(request, 'Invalid email/username or password')
                return render(request, self.template_name, {'form': form})

            user = authenticate(request, **kwargs, password=password)
            print(user)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to a dashboard or home page
            else:
                form=self.form_class()
                messages.error(request, 'Invalid email/username or password')
        return render(request, self.template_name, {'form': form})
    
@method_decorator(login_required(login_url='login'), name='dispatch')
class Dashboard(View):
    def get(self, request):
        context={
            'user': request.user
        }
        return render(request, 'users/dashboard.html',context=context)
    
@method_decorator(login_required(login_url='login'), name='dispatch')
class ProfileView(View):
    def get(self, request):
        context={
            'user': request.user
        }
        return render(request, 'users/profile.html',context=context)

class Logout(View):
    def post(self, request):
        logout(request)
        return redirect('login')

@method_decorator(login_required(login_url='login'), name='dispatch')
class ChangePasswordView(View):
    form_class = ChangePasswordForm
    template_name = 'users/change_password.html'

    def get(self, request):
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # for keeping the user logged in after password change
            messages.success(request, 'Your password was successfully updated.')
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})