from django.contrib.admin.filters import AllValuesFieldListFilter, RelatedFieldListFilter


class DropdownFilter(AllValuesFieldListFilter):
    template = "admin/dropdown.html"


class DropdownFilterForeignKey(RelatedFieldListFilter):
    template = "admin/dropdown.html"
