from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import SignupSerializer, UserUpdateSerializer, UserProfileSerializer
from django.contrib.auth import authenticate, logout, get_user_model # authenticate 로그인할 떄 필요함
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

User = get_user_model()


# @api_view : DRF 에서는 반드시 지정해주어야 한다.
# 지정하지 않으면 동작하지 않음
@api_view(['POST'])
@authentication_classes([])      # 전역 인증 설정 무시
@permission_classes([AllowAny])  # 전역 IsAuthenticated 설정 무시  # 회원가입된 유저만 사용가능한것을 무시
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "회원가입이 성공적으로 완료되었습니다."
        }, status=status.HTTP_201_CREATED) # 성공적일 경우
    return Response(serializer.errors, 
                    status=status.HTTP_400_BAD_REQUEST) # 실패할 경우

@api_view(['POST'])
@authentication_classes([])      # 전역 인증 설정 무시
@permission_classes([AllowAny])  # 전역 IsAuthenticated 설정 무시
def login(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    # 사용자 인증
    user = authenticate(request, email=email, password=password)
    if user is not None:
        # JWT 토큰 생성
        # 토큰 생성 후 반환 성공시에 로그인 성공
        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'message': '로그인 성공'
        }, status=200)
    else:
        return JsonResponse({'error': '이메일 또는 비밀번호가 올바르지 않습니다.'}, status=400)


@api_view(['POST'])
@authentication_classes([])      # 전역 인증 설정 무시
@permission_classes([AllowAny])  # 전역 IsAuthenticated 설정 무시
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token) # refresh_token을 블랙리스트에 넣어주면 로그아웃 가능
        token.blacklist() # jw_token 안에 로그인에 관한 정보가 있기때문에 블랙리스트에 넣어주면 로그아웃가능
        return Response({"message": "로그아웃 성공"})
    except Exception as e:
        return Response({"error": f"로그아웃 실패: {str(e)}"},  # 로그아웃 실패 이유 출력
                      status=status.HTTP_400_BAD_REQUEST)
        


# postman -> Authorization -> Bearer Token 경로에 로그인 access 토큰 붙여넣기
# 'PUT' : 전체 수정 
# 'PATCH' : 일부 수정
@api_view(['GET', 'PUT', 'PATCH'])
def profile(request):
    user = request.user  # JWT 인증을 통해 얻은 현재 사용자
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(user, context={'request': request})  # 절대주소가 담겨져있음
        return Response(serializer.data, status=200)
    
    if request.method in ('PUT', 'PATCH') :
        serializer = UserUpdateSerializer(instance=user, data=request.data, partial=True)  # partial=True로 일부 업데이트 허용

        if serializer.is_valid():
            serializer.save()  # 수정 내용 저장
            return Response({
                "message": "회원정보가 성공적으로 수정되었습니다.",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def follow(request, user_pk):
    profile_user = get_object_or_404(User, pk=user_pk)
    me = request.user
    
    if me == profile_user:   # 나를 팔로우할 시에
        return Response({'error': '자기 자신을 팔로우할 수 없습니다.'}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    if me.followings.filter(pk=profile_user.pk).exists(): # 이미 팔로우를 한 사람
        me.followings.remove(profile_user)
        is_followed = False
        message = f'{profile_user.email}님 팔로우를 취소했습니다.'
    else:
        me.followings.add(profile_user) #팔로우를 안한 사람
        is_followed = True
        message = f'{profile_user.email}님을 팔로우했습니다.'

    return Response({
        'is_followed': is_followed,
        'message': message,
    }, status=status.HTTP_200_OK)
