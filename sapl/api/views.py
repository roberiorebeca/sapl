from django.db.models import Q
from django.http import Http404
from rest_framework import mixins, viewsets
from rest_framework.generics import ListAPIView, GenericAPIView,\
    get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from sapl.api.serializers import ChoiceSerializer
from sapl.base.models import Autor, TipoAutor
from sapl.utils import SaplGenericRelation


class TipoAutorContentOfModelContentTypeView(ListAPIView):
    serializer_class = ChoiceSerializer
    permission_classes = (AllowAny,)
    queryset = TipoAutor.objects.all()
    model = TipoAutor
    pagination_class = None

    def get_queryset(self):
        queryset = ModelViewSet.get_queryset(self)
        if not self.kwargs['pk']:
            return queryset

        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])

        if not obj.content_type:
            raise Http404

        q = self.request.GET.get('q', '').strip()

        model_class = obj.content_type.model_class()

        fields = list(filter(
            lambda field: isinstance(field, SaplGenericRelation) and
            field.related_model == Autor,
            model_class._meta.get_fields(include_hidden=True)))

        assert len(fields) == 1

        fields_search = fields[0].fields_search

        if q:
            q_filter = Q()
            for fs in fields_search:
                q_filter |= Q(**{'%s__icontains' % fs: q})

            return model_class.objects.filter(q_filter)[:10]
        else:
            return model_class.objects.all()[:10]
