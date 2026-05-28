from django import forms
from .models import Content, Comment


class ContentForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '수정·삭제 시 사용할 비밀번호 (4자 이상)'
        }),
        label='수정용 비밀번호',
        min_length=4,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '비밀번호 확인'
        }),
        label='비밀번호 확인',
    )

    class Meta:
        model = Content
        fields = ['title', 'story', 'image', 'nickname', 'category']
        labels = {
            'title': '반려쓰레기의 이름',
            'story': '해방일지',
            'image': '사진',
            'nickname': '닉네임',
            'category': '어떻게 해방할까요?',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '이 물건의 이름이나 별명을 적어주세요',
            }),
            'story': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 12,
                'placeholder': (
                    '이 물건과의 이야기를 에세이 형식으로 자유롭게 써주세요.\n\n'
                    '언제부터 가지고 있었나요?\n'
                    '왜 버리지 못했나요?\n'
                    '이제 왜 보내려 하나요?\n\n'
                    '예: "2015년 첫 직장에서 받은 머그컵이다. 회사는 망했지만, 그 머그컵은 아직도 내 책상에 있다..."'
                ),
            }),
            'nickname': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '전시에 표시될 닉네임',
            }),
            'category': forms.RadioSelect(),
            'image': forms.FileInput(attrs={'class': 'form-file', 'accept': 'image/*'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('password')
        cpw = cleaned_data.get('confirm_password')
        if pw and cpw and pw != cpw:
            raise forms.ValidationError('비밀번호가 일치하지 않습니다.')
        return cleaned_data


class ContentEditForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'story', 'image', 'category']
        labels = {
            'title': '반려쓰레기의 이름',
            'story': '해방일지',
            'image': '사진 (변경 시에만 업로드)',
            'category': '어떻게 해방할까요?',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'story': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 12}),
            'category': forms.RadioSelect(),
            'image': forms.FileInput(attrs={'class': 'form-file', 'accept': 'image/*'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': ''}
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': '댓글을 입력하세요 (익명으로 표시됩니다)',
            })
        }


class PasswordVerifyForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '설정한 비밀번호를 입력하세요',
        }),
        label='비밀번호',
    )
