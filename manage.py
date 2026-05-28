#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pet_trash.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django를 불러올 수 없습니다. 'pip install -r requirements.txt'를 실행해 주세요."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
