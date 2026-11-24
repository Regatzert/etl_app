from django.urls import path

from .views import (
    EmployeeListView,
    DataQueryView,
)


urlpatterns = [
    path(
        "employees/",
        EmployeeListView.as_view(),
        name="employee-list",
    ),

    path(
        "<str:dataset>/",
        DataQueryView.as_view(),
        name="data-query"
    ),
]