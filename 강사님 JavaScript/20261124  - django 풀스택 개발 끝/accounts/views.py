from django.shortcuts import render, redirect

# article할때는 ModelForm
# auth할때는 built-in form 
from django.contrib.auth.forms import (
    AuthenticationForm, # 로그인을 위한 폼
    UserCreationForm, # 계정 생성 위한 폼 (회원가입)
    PasswordChangeForm # 비밀번호 변경을 위한 폼
)

# 로그인, 로그아웃 기능
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from .models import User


# 로그인 페이지를 띄우고 아이디 페스워드 입력하고 로그인버튼 누른다
def login(request):
    # 로그인버튼 누른다
    if request.method == 'POST':
        # AuthenticationForm : built-in form
        # request.POST : 아이디, 패스워드 (사용자가 입력한)
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            # get_user() : 인증된 사용자의 객체
            auth_login(request, form.get_user())
            return redirect('articles:index')
    else: # GET요청 X (POST요청이 아닐때)  
        form = AuthenticationForm() # 빈 폼
    # GET 요청 or 유효성 검사 실패했을때
    context = {
        'form': form
    }
    return render(request, 'accounts/login.html', context)



from django.contrib.auth.decorators import login_required

# 로그인한 사용자만 로그아웃 할수있도록
@login_required
def logout(request):
    auth_logout(request)
    # 로그아웃 페이지가 따로 있나요?? X
    return redirect('articles:index')

from .forms import CustomUserCreationForm, CustomUserChangeForm

def signup(request):
    # is_authenticated : 인증된 사용자라면 (로그인이 되어있는데 회원가입 버튼을 눌렀다면)
    if request.user.is_authenticated:
        return redirect('articles:index')

    if request.method == "POST": # submit버튼 눌렀을때
        # request.POST -> 내가 회원가입할때 입력한 정보들
        form = CustomUserCreationForm(request.POST)
        if form.is_valid(): # 1. 유효성검사
            user = form.save() # 2. DB에 저장
            auth_login(request, user) # 3. 로그인
            return redirect('articles:index')
        
    else: # POST요청이 아닐때
        form = CustomUserCreationForm() # 빈폼

    # 유효성 검사 실패했다 or 처음 회원가입페이지 들어갈때
    context = {
        'form': form
    }
    return render(request, 'accounts/signup.html', context)

# 로그인된 사용자만 회원탈퇴 할수있음
@login_required
def delete(request):
    # 현재 로그인 되어있는 user
    request.user.delete()
    return redirect('articles:index')

@login_required
def update(request):
    if request.method == "POST":
        # request.POST : 사용자가 작성한 (first_name, last_name, email)
        # request.user : 로그인되어있는 user
        form = CustomUserChangeForm(request.POST, instance = request.user)
        if form.is_valid():
            form.save()
            return redirect('articles:index')
    else: # POST요청이 아닐때 (submit 버튼 누르기 전)
        form = CustomUserChangeForm(instance = request.user)

    context = {
        'form': form
    }
    return render(request, 'accounts/update.html', context)


from django.contrib.auth import update_session_auth_hash

@login_required
def password(request):
  if request.method == 'POST':
    # 첫 번째 인자는 user, 두 번째 인자는 데이터
    form = PasswordChangeForm(request.user, request.POST)
    if form.is_valid():
      user = form.save()
      # 세션 무효화 방지(자동 로그아웃 방지)
      # hash 함수로 현재 사용자의 인증 세션 갱신
      update_session_auth_hash(request, user)
      return redirect('articles:index')
  else:
    form = PasswordChangeForm(request.user)
  context = {
    'form' : form,
  }
  return render(request, 'accounts/password.html', context)

from django.contrib.auth import get_user_model
# get_user_model() : 프로젝트에 활성화되어있는 모든 사용자 모델

def profile(request, username):
    User = get_user_model()
    # Person : 게시글 작성한 개인 사용자 (로그인한 사용자 X)
    person = User.objects.get(username=username)
    context = {
        'person': person
    }
    # 단순 GET요청 페이지 렌더링
    return render(request, 'accounts/profile.html', context)

from django.http import JsonResponse

@login_required
def follow(request, user_pk):
    User = get_user_model()
    # 나(me) <-> 상대방(you)
    # person : user_pk를 갖고 팔로우하려는 상대방
    you = User.objects.get(pk=user_pk)
    me = request.user
    # 자기자신을 팔로우 하는것을 방지
    if you != me :
        # filter.exist() : 데이터베이스(DB)에 존재하냐?
        # followers : 역참조
        if me in you.followers.all():
            # 이미 팔로우했으면 팔로우 취소
            you.followers.remove(me)
            is_followed = False
        else:
            # 팔로우
            you.followers.add(me)
            is_followed = True

        context = {
            'is_followed' : is_followed,
            'followings_count' : you.followings.count(),  #- 팔로잉 수
            'followers_count' : you.followers.count(),   #- 팔로워 수
        }
        return JsonResponse(context)

    return redirect('accounts:profile', person.username)
