import os
import secrets


def get_filename(path):  # /abc/filename.mp4
    return os.path.basename(path)


def random_string_generator():
    allowed_char = "0123456789abcdefghijklmnopqrstuvwxyz"
    return ''.join(secrets.choice(allowed_char) for i in range(5))


def generate_unique_referral_token(instance):
    token = random_string_generator()
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(ref=token)
    if qs_exists.exists():
        return random_string_generator()
    return token


def generate_phone_code():
    random_number = '0123456789'
    generated = ''.join(secrets.choice(random_number) for i in range(4))
    return generated


def random_token_generator():
    allowed_char = "0123456789abcdefghijklmnopqrstuvwxyz"
    return ''.join(secrets.choice(allowed_char) for i in range(15))


def generate_unique_billing_token(instance):
    token = random_token_generator()
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(user_token=token)
    if qs_exists.exists():
        return random_token_generator()
    return token

