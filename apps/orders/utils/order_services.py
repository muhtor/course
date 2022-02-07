from random import randint


def unique_order_id_generator(instance):
    order_new_id = random_order_id_generator()
    Klass = instance.__class__
    while Klass.objects.filter(order_id=order_new_id).exists():
        order_new_id = random_order_id_generator()
    return order_new_id


def random_order_id_generator(order_prefix="10", digit_count=8):
    random_number = randint(10 ** digit_count, 10 ** (digit_count + 1) - 1)
    order_id = "{}{}".format(order_prefix, random_number)
    return order_id

