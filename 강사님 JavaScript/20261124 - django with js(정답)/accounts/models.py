from django.db import models

# Create your models here.
# AbstracUser : Auth관련 기본적인 필드를 제공
from django.contrib.auth.models import AbstractUser

# symmetrical=False : 내가 팔로잉 했다고 상대방이 나를 팔로우 한것은 아니다.
class User(AbstractUser):
    followings = models.ManyToManyField(
        'self', symmetrical=False, related_name='followers'
    )