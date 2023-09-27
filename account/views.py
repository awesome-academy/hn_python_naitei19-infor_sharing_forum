from django.shortcuts import render
from .forms import SignUpForm, SignInForm, PasswordResetForm, SetPasswordForm, UserEditForm, ChangePasswordForm
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.db.models.query_utils import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
import re
from .tokens import account_activation_token

from app.models import Follow, Post, Bookmark, Comment, PostReaction, HashTag
from app.views import get_paginated_object_list

# clean all html tags in message
def clean_message(text):
    return re.sub('<[^<]+?>', '', str(text))

def activateEmail(request, user, to_email):
    mail_subject = 'Kích hoạt tài khoản'
    message = render_to_string('account/activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Chúng tôi đã gửi link kích hoạt tài khoản cho bạn thông qua email.')
    else:
        messages.error(request, f'Đã có lỗi xảy ra trong quá trình gửi mail. Vui lòng thử lại sau.')

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Kích hoạt tài khoản thành công!')
        return redirect('signin')
    else:
        messages.error(request, 'Link kích hoạt tài khoản không hợp lệ!')
    
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            messages.success(request, _('Đăng ký thành công!'))
            activateEmail(request, user, request.POST['email'])
            return redirect('home')
        else:
            for error in list(form.errors.values()):
                messages.error(request, clean_message(error))
    else:
        form = SignUpForm()
    return render(request, 'account/signup.html', {'form': form})
        
def signin(request):
    if request.user.is_authenticated:
        messages.info(request, _('Bạn đã đăng nhập rồi!'))
        return redirect('home')
    
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            user = authenticate(username = request.POST['username'], password = request.POST['password'])
            if user is not None:
                login(request, user)
                messages.success(request, _('Đăng nhập thành công!'))
                return redirect('home')
        else:
            for error in list(form.errors.values()):
                messages.error(request, clean_message(error))
    else:
        form = SignInForm()
    return render(request, 'account/signin.html', {'form': form})

def signout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, _('Đăng xuất thành công!'))
    else:
        messages.info(request, _('Bạn chưa đăng nhập!'))
    return redirect('home')

def password_reset_request(request):
    if request.user.is_authenticated:
        messages.warning(request, 'Bạn đang đăng nhập!!!')
        return redirect('home')
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Đặt lại mật khẩu"
                message = render_to_string("account/template_reset_password.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(request, "Chúng tôi đã gửi email để reset mật khẩu của bạn")
                else:
                    messages.error(request, "Đã có lỗi xảy ra trong quá trình gửi mail. Vui lòng thử lại sau.")
                return redirect("home")
            else:
                messages.error(request, "Không có tài khoản nào được liên kết với email này")
        else:
            for error in list(form.errors.values()):
                messages.error(request, clean_message(error))
    else:
        form = PasswordResetForm()
    
    return render(request=request, template_name="account/password_reset.html", context={"form":form})

def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Đặt lại mật khẩu thành công. Bạn có thể đăng nhập bằng mật khẩu mới.")
                return redirect('signin')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, clean_message(error))
        else:
            form = SetPasswordForm(user)
            return render(request, 'account/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn!")

    messages.error(request, 'Đã có lỗi xảy ra trong quá trình đặt lại mật khẩu. Vui lòng thử lại sau.')
    return redirect("home")

def show_profile(request, username):
    request_user = get_user_model().objects.filter(username=username).first()
    if request_user is None:
        messages.error(request, 'Không tìm thấy tài khoản này!')
        return redirect('home')
    else:
        follow = _get_follower_followed(request, request_user)
        posts = _get_post(request, request_user)

        # request_user.current_user_following = follow['current_user_following'] if request.user.is_authenticated else ''

        context = {
            'follow': follow,
            'posts': posts,
            'request_user': request_user
        }

        return render(request, 'account/profile.html', context)

# Get following, followed of request user
def _get_follower_followed(request, request_user, num_each_page=12):
    # Get current user
    current_user = request.user
    # GET page number
    page_following = request.GET.get('page_following')
    page_followed = request.GET.get('page_followed')
    
    # Get following, followed of request user
    following = Follow.objects.filter(follower=request_user)
    followed = Follow.objects.filter(followed=request_user)

    following_paginator = Paginator(following, num_each_page)
    followed_paginator = Paginator(followed, num_each_page)

    following = get_paginated_object_list(following_paginator, page_following)
    followed = get_paginated_object_list(followed_paginator, page_followed)

    # Check if current user is following request user
    if current_user.is_authenticated:
        current_user_following = Follow.objects.filter(follower=current_user, followed=request_user).first()
    
    # count follower, post of following, followed
    for var in [following, followed]:
        for index, item in enumerate(var):
            if var == following:
                var[index].num_follower = Follow.objects.filter(followed=item.followed).count()
                var[index].num_post = Post.objects.filter(user=item.followed).count()
                if current_user.is_authenticated:
                    var[index].is_following = Follow.objects.filter(follower=current_user, followed=item.followed).first()
            else:
                var[index].num_follower = Follow.objects.filter(followed=item.follower).count()
                var[index].num_post = Post.objects.filter(user=item.follower).count()
                if current_user.is_authenticated:
                    var[index].is_following = Follow.objects.filter(follower=current_user, followed=item.follower).first()

    context = {
        'following': following,
        'followed': followed
    }

    request_user.current_user_following = current_user_following if current_user.is_authenticated else ''

    return context

def _get_post(request, request_user, num_each_page=10):
    # Get page number
    page_number = request.GET.get('page_post')

    # Get posts of request user
    if request_user == request.user:
        posts = Post.objects.filter(user=request_user, status__in=[0, 1, 3])
    else:
        posts = Post.objects.filter(user=request_user, status=1)

    posts = posts.order_by('-created_at')

    posts = Paginator(posts, num_each_page)

    posts = get_paginated_object_list(posts, page_number)

    for index, post in enumerate(posts):
        # View count
        posts[index].view_count = int(post.view_count)

        # Bookmark count
        posts[index].bookmark_count = Bookmark.objects.filter(post=post).count()

        # Comment count
        posts[index].comment_count = Comment.objects.filter(post=post).count()

        # Calculate reaction point with feedback_value
        posts[index].reaction_point = 0
        reactions = PostReaction.objects.filter(post=post)
        for reaction in reactions:
            posts[index].reaction_point += reaction.feedback_value

    return posts

@login_required
def edit_profile(request, username):
    request_user = get_user_model().objects.filter(username=username).first()
    if request_user != request.user:
        messages.error(request, _('Bạn không thể chỉnh sửa thông tin của người khác!'))
        return redirect('home')
    if request_user is None:
        messages.error(request, _('Không tìm thấy tài khoản này!'))
        return redirect('home')
    else:
        if request.method == 'POST':
            form = UserEditForm(request.POST, instance=request_user)
            if form.is_valid():
                form.save()
                messages.success(request, _('Cập nhật thông tin thành công!'))
                return redirect('profile', username=request_user.username)
            else:
                for error in list(form.errors.values()):
                    messages.error(request, clean_message(error))
        else:
            form = UserEditForm(instance=request_user)
        return render(request, 'account/edit_profile.html', {'form': form})

@login_required
def change_password(request, username):
    request_user = get_user_model().objects.filter(username=username).first()
    if request_user != request.user:
        messages.error(request, _('Bạn không thể chỉnh sửa thông tin của người khác!'))
        return redirect('home')
    if request_user is None:
        messages.error(request, _('Không tìm thấy tài khoản này!'))
        return redirect('home')
    else:
        if request.method == 'POST':
            form = ChangePasswordForm(request.POST)
            if form.is_valid():
                if request.user.check_password(request.POST['old_password']):
                    request.user.set_password(request.POST['new_password'])
                    request.user.save()

                    # Keep user login
                    update_session_auth_hash(request, request.user)

                    messages.success(request, _('Đổi mật khẩu thành công!'))
                    return redirect('profile', username=request.user.username)
                else:
                    messages.error(request, _('Mật khẩu cũ không đúng!'))
            else:
                for error in list(form.errors.values()):
                    messages.error(request, clean_message(error))
        else:
            form = ChangePasswordForm()
        return render(request, 'account/change_password.html', {'form': form})
