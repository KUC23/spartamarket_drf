#accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Follow


User = get_user_model()



# 회원 가입 검증을 위한 클래스
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True) # 한번더 확인용

    class Meta:
        model = User # 유저 모델을 사용
        fields = ('email', 'password', 'password2', 'username', 'profile_image')# models.py에 정의했으므로 프로필 이미지는 공백가능

    def validate(self, data):
        # 비밀번호 1과 2가 일치하지 않는다면,
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                "password": "비밀번호가 일치하지 않습니다."
            })
        return data

    def create(self, validated_data): 
        validated_data.pop('password2')  # 단순한 확인용이기때문에 제거해준다.
        return User.objects.create_user(**validated_data)





# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['email', 'username', 'profile_image']  # 반환할 필드

class UserProfileSerializer(serializers.ModelSerializer):
    # FollowSerializer 는 따로 써줘도 상관없지만 profile을 조회할때 같이 보여지는게 좋다고 판단되면 같이 써주는게 좋다.
    class FollowSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("id", "email", "username", "profile_image")

    followers = FollowSerializer(many=True, read_only=True)
    followings = FollowSerializer(many=True, read_only=True)
    follower_count = serializers.IntegerField(source='followers.count', read_only=True)   # 팔로워 수
    following_count = serializers.IntegerField(source='followings.count', read_only=True) # 팔로잉 수
    profile_image = serializers.SerializerMethodField()  # 커스텀 필드로 처리
    
    class Meta:
        model = User
        fields = ['email', 'username','name','birthday','gender','introduce', 'profile_image', 'followings', 'followers', 'follower_count', 'following_count']  # 반환할 필드

    # 장고에서 제공해주는 프로필 이미지로 경로가 지정되기때문에
    # 절대 경로로 바꿔줘야한다.        
    def get_profile_image(self, obj):
        request = self.context.get('request')  # Serializer context에서 request 가져오기
        if obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url)
        return None





class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User                            # User 에서 가져온 정보는 
        fields = ('username', 'profile_image')  # 수정 가능한 필드
                                                # 여기서 지정한 필드만 수정가능함