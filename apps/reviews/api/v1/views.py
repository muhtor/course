from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ....courses.models import Course
from rest_framework.views import APIView
from ....core.api.response import ReviewPaginationResponse
from ...models import Review
from .serializers import ReviewSerializer


class ReviewCreateListView(APIView, ReviewPaginationResponse):
    # permission_classes = (IsAuthenticated, )
    serializer_class = ReviewSerializer

    def get(self, request, *args, **kwargs):
        # http://127.0.0.1:2000/api/reviews/v1/review-list/{id}
        qs = Course.objects.filter(pk=int(self.kwargs['pk']))
        if qs.exists():
            try:
                course = qs.first()
                queryset = Review.objects.filter(course_id=course.id).order_by('-id')
                average_rate = 0
                if queryset.count() != 0:
                    average_rate = queryset.aggregate(tot=Sum('rates'))['tot'] / queryset.count()   # float
                result = self.paginated_queryset(queryset, request)
                serializer = self.serializer_class(result, many=True)
                response = self.paginated_response(status=True, code=800, rate=round(average_rate, 1), data=serializer.data)
                return Response(response.data)
            except Exception as e:
                return Response({'success': False, 'code': 807, 'error': e.args})
        return Response({'success': False, 'code': 804, 'error': f"{int(self.kwargs['pk'])} курс не найден"})

    def post(self, request):
        data = request.data
        # http://127.0.0.1:2000/api/reviews/v1/review-create
        try:
            course = Course.objects.get(pk=data['course_id'])
            serializer = ReviewSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save(course=course, user=request.user)
                return Response({"success": True, "code": 801, "data": serializer.data})
            return Response({'success': False, 'code': 803, 'error': serializer.errors})
        except Exception as e:
            return Response({'success': False, 'code': 804, 'error': e.args})
