from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from contents.models import Content
from PIL import Image, ImageDraw
from io import BytesIO

SAMPLE_DATA = [
    {
        'title': '초등학교 졸업 앨범',
        'story': (
            '1998년 초등학교를 졸업하던 날, 담임 선생님께서 직접 사진을 찍어주셨다. '
            '표지가 낡고 페이지마다 곰팡이 냄새가 나지만, 어린 내 얼굴이 거기 있다. '
            '이사할 때마다 챙겼고, 이십 년 넘게 책장 제일 구석에 꽂혀 있었다.\n\n'
            '가끔 꺼내 보다가 다시 꽂는다. 그러기를 반복하다 어느 날 생각했다. '
            '나는 정말 다시 이 앨범을 펼쳐볼까? 솔직히 잘 모르겠다. '
            '하지만 버리지도 못하겠다. 그 안에 있는 건 추억이 아니라 그냥 시간인 것 같아서.\n\n'
            '결국 오늘 이렇게 사진을 찍고, 이야기를 남긴다. '
            '물건은 보내더라도 이 기록만큼은 남아있으면 좋겠다.'
        ),
        'nickname': '서울 촌놈',
        'category': 'immediate_trash',
        'bg': (245, 235, 210),
        'fg': (140, 110, 70),
    },
    {
        'title': '첫 월급으로 산 머그컵',
        'story': (
            '2012년 첫 직장에서 받은 첫 월급. 뭔가 기념이 될 물건을 사고 싶었다. '
            '백화점을 두 시간 돌다가 고른 게 이 흰 머그컵이었다.\n\n'
            '그 회사는 3년 만에 문을 닫았고, 나는 다섯 번 이직했다. '
            '그런데 이 컵은 아직도 내 책상에 있다. 매일 아침 커피를 마신다. '
            '이걸 버리면 그때의 나를 버리는 것 같아서, 계속 쓴다.\n\n'
            '오프라인 전시에서 누군가의 책상 위에 놓이면 좋겠다. '
            '새로운 첫 월급의 기억과 함께.'
        ),
        'nickname': '직장인 A',
        'category': 'immediate_exhibition',
        'bg': (210, 225, 245),
        'fg': (60, 90, 140),
    },
    {
        'title': '전 남자친구가 준 곰인형',
        'story': (
            '4년을 사귀었다. 헤어진 지도 벌써 3년이 됐다. '
            '인형은 침대 한쪽 구석에 여전히 앉아 있다.\n\n'
            '버리려고 쓰레기봉투에 넣은 적도 있었는데, 결국 꺼냈다. '
            '왜인지 모르겠다. 그 사람이 그리워서는 아닌 것 같은데. '
            '어쩌면 그냥 그 시절이 그리운 건지도. '
            '이십대 중반, 아무것도 몰랐던 그때.\n\n'
            '이제 삼십이 됐고, 새 사람도 생겼는데, 인형은 아직 거기 있다. '
            '버려야 할까, 아직 더 있어도 될까. 여러분이 결정해 주세요.'
        ),
        'nickname': '봄날의 곰',
        'category': 'temporary_storage',
        'bg': (250, 215, 220),
        'fg': (160, 70, 90),
    },
    {
        'title': '아버지의 낡은 공구함',
        'story': (
            '아버지가 돌아가시고 집을 정리하면서 가져왔다. '
            '낡은 철제 공구함. 안에는 드라이버 세 개, 망치 하나, 줄자, '
            '그리고 내가 어릴 때 고장 난 장난감을 고쳐주시던 작은 펜치.\n\n'
            '아버지는 뭐든 직접 고치는 분이었다. '
            '나는 그 반대라 뭐가 고장 나면 그냥 새로 산다. '
            '공구함을 쓸 일이 없다. 그런데 버릴 수가 없다.\n\n'
            '이게 아버지의 손때가 가장 많이 묻은 물건이라서. '
            '이 공구함을 버리는 날이 진짜 마지막 작별 같아서. '
            '전시에서 이 물건의 이야기를 들어줄 누군가를 찾습니다.'
        ),
        'nickname': '막내아들',
        'category': 'immediate_exhibition',
        'bg': (205, 215, 200),
        'fg': (60, 90, 60),
    },
]


def make_placeholder_image(bg_color, fg_color, size=800):
    img = Image.new('RGB', (size, size), color=bg_color)
    draw = ImageDraw.Draw(img)

    # 바깥 테두리
    margin = 32
    draw.rectangle(
        [margin, margin, size - margin, size - margin],
        outline=fg_color + (120,) if len(fg_color) == 3 else fg_color,
        width=1,
    )
    # 안쪽 테두리
    draw.rectangle(
        [margin + 8, margin + 8, size - margin - 8, size - margin - 8],
        outline=fg_color,
        width=1,
    )

    buf = BytesIO()
    img.save(buf, format='JPEG', quality=88)
    buf.seek(0)
    return buf.read()


class Command(BaseCommand):
    help = '샘플 콘텐츠 4개를 생성합니다 (콘텐츠가 없을 때만 실행)'

    def handle(self, *args, **options):
        if Content.objects.exists():
            self.stdout.write('콘텐츠가 이미 존재합니다. 샘플 생성을 건너뜁니다.')
            return

        for i, data in enumerate(SAMPLE_DATA):
            img_bytes = make_placeholder_image(data['bg'], data['fg'])

            content = Content(
                title=data['title'],
                story=data['story'],
                nickname=data['nickname'],
                category=data['category'],
                status='approved',
            )
            content.set_password('sample1234')
            content.image.save(
                f'sample_{i + 1}.jpg',
                ContentFile(img_bytes),
                save=False,
            )
            content.save()
            self.stdout.write(f'  ✓ 생성: {data["title"]} ({data["category"]})')

        self.stdout.write(self.style.SUCCESS('샘플 콘텐츠 4개 생성 완료!'))
