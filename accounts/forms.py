from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, ProjectCode


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='이메일')
    member_type = forms.ChoiceField(
        choices=[('regular', '일반 회원'), ('project', '프로젝트 참여회원')],
        widget=forms.RadioSelect,
        label='가입 유형',
        initial='regular',
    )
    project_code = forms.CharField(
        required=False,
        label='회원코드',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '프로젝트 참여회원 전용 코드를 입력하세요',
        }),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'member_type', 'project_code']
        labels = {'username': '아이디'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ('member_type',):
                field.widget.attrs.setdefault('class', 'form-input')
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def clean(self):
        cleaned_data = super().clean()
        member_type = cleaned_data.get('member_type')
        code_input = cleaned_data.get('project_code', '').strip()

        if member_type == 'project':
            if not code_input:
                raise forms.ValidationError('프로젝트 참여회원은 회원코드를 입력해야 합니다.')
            if not ProjectCode.objects.filter(code=code_input).exists():
                raise forms.ValidationError('유효하지 않은 회원코드입니다.')

        return cleaned_data


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'
        self.fields['username'].label = '아이디'
        self.fields['password'].label = '비밀번호'
