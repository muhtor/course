# from django.core.exceptions import ObjectDoesNotExist
# from decimal import Decimal
# import secrets
from decimal import Decimal

from django.db.models import F
from rest_framework.response import Response

from ..models import Cart, CartCourse, Course
from ...courses.models import CertificatedCourse


def get_invalid_course_id(obj_id: int, user) -> int:
    """If the course is already paid by the user/Does not exist return them"""
    try:
        course = Course.objects.get(id=obj_id)
    except Course.DoesNotExist:
        return obj_id

    if CartCourse.objects.filter(cart__user=user, paid=True, course=course).exists():
        return obj_id


class Queries:

    def data_is_valid(self, items, user):
        invalid_id = False
        for obj_id in items:
            invalid_id = get_invalid_course_id(obj_id, user)

        if invalid_id:
            return dict(is_valid=False, invalid_id=invalid_id, items=[])
        else:
            return dict(is_valid=True, invalid_id=0, items=items)


def create_cart_courses(
    courses_id: list,
    cart: Cart,
    certificated_course: CertificatedCourse = None
) -> float:
    """
    :param certificated_course: if the courses have a certificated course
    :return total price of the created cart courses
    """
    total = 0
    for course_id in courses_id:
        course = Course.objects.get(id=course_id)
        item, created = CartCourse.objects.get_or_create(
            insert_type="UNPAID",
            cart=cart,
            course=course,
            certificated_course=certificated_course,
            defaults={'course': course}
        )
        if created:
            total += course.price
    return total


def create_cart_certificated_courses(certificated_courses_id: list, cart: Cart):
    """:return total price of the all certificated courses"""
    total = 0

    for id_ in certificated_courses_id:
        certificated_course = CertificatedCourse.objects.get(id=id_)
        courses = certificated_course.get_unpaid_courses(
            user=cart.user
        )[0].exclude(cartcourse__cart__exact=cart.id).values_list('id', flat=True)

        courses_total = create_cart_courses(courses, cart, certificated_course)
        if courses_total:
            total += certificated_course.get_price_for_user(cart.user)

    return total


def increase_cart_total(cart: Cart, total: float) -> None:
    Cart.objects.filter(id=cart.id).update(
        subtotal=F('subtotal') + total,
        total=F('total') + total
    )
    cart.refresh_from_db()


def add_cart_items(
    courses_id: list,
    certificated_courses_id: list,
    cart: Cart
) -> None:
    """Return total price for all added cart items"""
    total = Decimal(0)
    total += create_cart_courses(courses_id, cart)
    total += create_cart_certificated_courses(certificated_courses_id, cart)
    increase_cart_total(cart, total)


def remove_cart_course(cart_course: CartCourse) -> float:
    """:return price of the course"""
    price_to_remove = cart_course.course_price
    cart_course.delete()
    return price_to_remove


def remove_cart_certificated_course(cart_course: CartCourse, cart: Cart) -> float:
    """Delete the cart_course and all certificated course sub courses
    from the cart and create the new CartCourse's without the deleted

    :param cart_course: cart course to remove (contains a certificated course)
    :return total price to decrease

    """
    certificated_course = CertificatedCourse.objects.get(
        id=cart_course.certificated_course.id
    )

    CartCourse.objects.filter(
        course_id__in=certificated_course.sub_courses.values_list('id', flat=True),
        cart=cart,
        insert_type="UNPAID"
    ).delete()

    courses_to_add = certificated_course.sub_courses.exclude(
        id=cart_course.course.id
    ).values_list('id', flat=True)

    whole_price = certificated_course.get_price_for_user(cart.user)
    return whole_price - create_cart_courses(courses_to_add, cart)


def remove_cart_item(course_id: int, cart: Cart) -> None:
    """Removes course or certificated course from the cart.
    Updates the cart price
    """
    cart_course = CartCourse.objects.get(
        course_id=course_id,
        cart=cart,
        insert_type="UNPAID"
    )
    if cart_course.certificated_course:
        price_to_remove = remove_cart_certificated_course(cart_course, cart)
    else:
        price_to_remove = remove_cart_course(cart_course)

    increase_cart_total(cart, -float(price_to_remove))


def handle_error_response(error_code: int = 404):
    def wrapper(func):
        def inner(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
            except Exception as e:
                return Response({
                    "success": False,
                    "code": error_code,
                    "message": e.args
                })
            return res
        return inner
    return wrapper
