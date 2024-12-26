from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from datetime import date


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # 이메일 작성이 안됐을 경우
        if not email:
            raise ValueError('이메일은 필수입니다')
        email = self.normalize_email(email) # 공백제거, 소문자롤 변환
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    # 관리자계정
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    




# Create your models here.
class User(AbstractUser):
    email = models.EmailField('이메일', unique=True)
    username = models.CharField('닉네임', max_length=150,blank=False, null=False)
    profile_image = models.ImageField('프로필 이미지', upload_to='profile_images/', blank=True, null=True)
    name = models.CharField('이름', max_length=150,blank=False, null=False,default='unknown')
    birthday = models.DateField('생일',
                                help_text="YYYY-MM-DD 형식으로 입력해주세요",
                                blank=False,default=date(2000, 1, 1))
    gender = models.CharField(
        max_length=6,  # 'male', 'female', 'other' 최대 길이에 맞춰서 6으로 설정
        choices=[('male', 'Male'), ('female', 'Female')],
        blank=True  # 선택적으로 입력 가능
    )
    introduce = models.CharField('자기소개',max_length=150, blank=True)


    # ManyToManyField로 팔로우 기능 구현
    followings = models.ManyToManyField(
        'self',                   # 자기 자신과의 관계
        symmetrical=False,        # 대칭 관계가 아님 (단방향)
        related_name='followers', # 역참조 이름
        through='Follow',         # 중간 테이블
        blank= True
    )




    USERNAME_FIELD = 'email'    # 로그인시 필요한 필드
    REQUIRED_FIELDS = ['username', 'name', 'birthday']        # 필수 필드 정의 

    objects = CustomUserManager()
    

    def __str__(self):
        return self.email
    


# 중간 테이블을 명시적으로 정의
class Follow(models.Model):
    follower = models.ForeignKey(
        User, related_name='followed_users', on_delete=models.CASCADE)  # 팔로우를 하는 사용자
    following = models.ForeignKey(
        User, related_name='following_users', on_delete=models.CASCADE)  # 팔로우받는 사용자
    created_at = models.DateTimeField(auto_now_add=True)  # 팔로우한 시간

    class Meta:
        unique_together = ('follower', 'following')  # 중복 팔로우 방지

    def __str__(self):
        return f"{self.follower} follows {self.following}"