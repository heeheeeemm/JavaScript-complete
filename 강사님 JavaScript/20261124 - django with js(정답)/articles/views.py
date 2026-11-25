from django.shortcuts import render, redirect

# Create your views here.

# 현재 티렉토리에서 models.py로부터 Aritlce모델 가져오겠다.
from .models import Article, Comment

from django.contrib.auth.decorators import login_required

def index(request):
    # QuerySet API ---> 전체 데이터 조회
    # Article.objects.all()
    articles = Article.objects.all()

    context = {
        'articles': articles
    }
    # articles폴더의 index.html 파일을 랜더링하겠다
    return render(request, 'articles/index.html', context)

def detail(request, pk):
    # QuerySet API ---> 단일 게시글 조회 : get
    article = Article.objects.get(pk = pk)

    comment_form = CommentForm()
    # 역참조 (게시글에서 댓글 가져오기 - 외래키가 댓글에있음)
    comments = article.comment_set.all()

    context = {
        'article': article,
        'comment_form': comment_form,
        'comments': comments,
    }
    return render(request, 'articles/detail.html', context)

from django.shortcuts import render, redirect
from .forms import ArticleForm, CommentForm


def create(request):
    # 1. 내가 게시글 생성 버튼 눌렀을때 (POST 요청)
    if request.method == 'POST':
        # print(request.POST) -> title, content
        # request.FILES -> 업로드한 데이터
        form = ArticleForm(request.POST, request.FILES)
        # 유효성 검사
        if form.is_valid(): # 주관식 단골 문제 (스펠링 많이 틀림 주의!!)
            # 바로 DB에 저장하지 않고(중간 단계를 거쳐서 저장)
            article = form.save(commit=False)
            # 로그인한 사용자(request.user)
            article.user = request.user
            # DB에 저장
            article.save()
            return redirect('articles:detail', article.pk)


    # 2. POST요청이 아닐때 -> 게시글 생성 버튼 누르기전 or 유효성검사 실패했을 때
    else:
        form = ArticleForm()
        # GET 요청인 경우
    context = {
        'form': form
    }
    return render(request, 'articles/create.html', context)






# 리다이렉트 : (CREATE와 차이 : 기존에 있던 게시글을 변경)
def update(request, pk):
    # 우선 기존에 있던 게시글을 조회 (QuerySetAPI)
    article = Article.objects.get(pk =pk)

    # 1. POST요청일때
    if request.method == 'POST':
        # instance = article (기존에있던 데이터를 미리 채우기)
        form = ArticleForm(request.POST, request.FILES, instance = article)
        # 유효성 검사
        if form.is_valid():
            form.save()
            return redirect('articles:detail', article.pk)

    # 2. POST요청이 아닐때
    else:
        form = ArticleForm(instance = article)

    # GET 요청
    context = {
        'article': article,
        'form': form
    }
    return render(request, 'articles/update.html', context)

# POST요청 -> 리다이렉트
def delete(request, pk):
    # 조회후 삭제
    article = Article.objects.get(pk = pk)
    article.delete()
    return redirect('articles:index')



@login_required
def comments_create(request, pk):
    # 게시글 조회 - QuerySetAPI
    article = Article.objects.get(pk=pk)
    # request.POST -> content (댓글 내용)
    comment_form = CommentForm(request.POST)
    # 유효성 검사
    if comment_form.is_valid():
        comment = comment_form.save(commit=False) # 바로 DB에 저장 x
        comment.article = article # 1. 게시글의 객체
        comment.user = request.user # 2. 로그인한 사용자
        comment.save() # 3. DB에 저장
        return redirect('articles:detail', article.pk)
    # 유효성 검사 실패
    context = {
        'article': article,
        'comment_form': comment_form
    }
    return render(request, 'articles/detail.html', context)

@login_required
def comments_delete(request, article_pk, comment_pk):
    comment = Comment.objects.get(pk=comment_pk)
    # 내가아닌 다른유저가 삭제못하게(로그인한유저 == 댓글작성한유저)
    if request.user == comment.user:
        comment.delete()
    return redirect('articles:detail', article_pk)


from django.http import JsonResponse

@login_required
def likes(request, article_pk):
    article = Article.objects.get(pk=article_pk)
    # 좋아요 <-> 좋아요취소
    # 현재 로그인한 사용자가 이미 좋아요를 눌렀는지 확인
    if request.user in article.like_users.all():
        # 이미 좋아요 눌렀으면 좋아요 취소
        article.like_users.remove(request.user)
        is_liked = False
    else: # 좋아요 누르지 않았다면 좋아요
        article.like_users.add(request.user)
        is_liked = True
    context = {
        'is_liked' : is_liked
    }
    return JsonResponse(context)
    
