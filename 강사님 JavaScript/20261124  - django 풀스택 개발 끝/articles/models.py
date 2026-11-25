from django.db import models

from django.conf import settings

# Create your models here.
class Article(models.Model):
    # 외래키 - Many-to-one
    # on_delete=models.CASCADE ---> 사용자가 회원탈퇴하면 게시글도 함께 삭제
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name = 'like_articles'
    )

    # 게시글 제목은 악용의 위험이 있기때문에 글자 제한을 둔다
    title = models.CharField(max_length=20)
    content = models.TextField()

    # 게시글 쓸때 보통 이미지는 필수가 아니다
    image = models.ImageField(blank=True)

    # auto_now_add : 객체가 처음 생성되는 시간
    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now : 객체가 저장 될때마다 시간
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    # 게시글과 댓글간의 관계 (Many-to-one) 
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    # 작성자와 댓글간의 관계 (Many-to-one)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)