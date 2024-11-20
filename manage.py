# #!/usr/bin/env python
# """Django's command-line utility for administrative tasks."""
# import os
# import sys


# def main():
#     """Run administrative tasks."""
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
#     try:
#         from django.core.management import execute_from_command_line
#     except ImportError as exc:
#         raise ImportError(
#             "Couldn't import Django. Are you sure it's installed and "
#             "available on your PYTHONPATH environment variable? Did you "
#             "forget to activate a virtual environment?"
#         ) from exc
#     execute_from_command_line(sys.argv)

#     port = int(os.environ.get("PORT", "8000"))  # Default to 8000 if PORT is not set
#     os.system(f"python manage.py runserver 0.0.0.0:{port}")


# if __name__ == '__main__':
#     main()


import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    if len(sys.argv) == 1 or sys.argv[1] != "runserver":
        execute_from_command_line(sys.argv)
    else:
        port = os.environ.get("PORT", "8000")
        sys.argv += [f"0.0.0.0:{port}"]
        execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
