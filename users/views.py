from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth import authenticate, login
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from users.email import send_forgot_email
from .forms.user_form import ChangePasswordForm, CustomUserCreationForm, ForgotPasswordForm, LoginForm, ResetPasswordForm
import re
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from .models import CustomUser
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout

class RegisterView(View):
    '''
    Basic Registration view for user, using django built in Authentication :)
    '''
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
    '''
    Custom Login View for user, using django built in Authentication :)
    '''
    template_name = 'users/login.html'
    form_class = LoginForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
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
    

class ForgotPassword(View):
    '''
    View to reset password can be accessed by anaonymous user to rest password over mail
    '''
    form_class = ChangePasswordForm
    template_name = 'users/forgot_pass.html'
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = ForgotPasswordForm()
        return render(request, self.template_name, {'form': form})
    
    ## Not Using Django PasswordResetView as to show my understanding and custom is better
    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.get(email=email) ## Get as we already checked if user exsists
            uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            link = f"{settings.BASE_URL}reset-password?base={uidb64}&token={token}"
            send_forgot_email(request,user.username, user.email, link)
            messages.success(request, 'We have sent you a link to reset your password.')
            return redirect('login')
        return render(request, self.template_name, {'form': form})
    
 ## Not Using Django PasswordResetView as to show my understanding and custom is better
class PasswordResetView(View):
    form_class = ResetPasswordForm
    template_name = 'users/reset_password.html'

    def get(self, request, *args, **kwargs):
        uidb64 = request.GET.get('base', None)
        token = request.GET.get('token', None)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            form = self.form_class(user=user)
            return render(request, self.template_name, {'form': form, 'validlink': True})
        else:
            return render(request, self.template_name, {'validlink': False})

    def post(self, request, *args, **kwargs):
        uidb64 = request.GET.get('base', None)
        token = request.GET.get('token', None)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            form = self.form_class(data=request.POST, user=user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password was reset successfully.')
                return redirect('login')
            else:
                
                return render(request, self.template_name, {'form': form, 'validlink': True})
        else:
            return render(request, self.template_name, {'validlink': False})