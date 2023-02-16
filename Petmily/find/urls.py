from django.urls import path
from .import views
from django.views.generic import TemplateView
# from board.views import list


urlpatterns = [
    # board
    path("index/", views.home, name="find_index"),

    path("detail/<int:pk>/", views.detail, name="find_detail"),
    path("write", views.update, name="find_write"),
    path("delete/<int:pk>/", views.remove, name="find_remove"),
    path("edit/<int:pk>/", views.edit, name="find_edit"),

    # 댓글
    path("comment/create/<int:pk>/", views.comment_create,
         name="find_comment_create"),

    path("<int:post_pk>/comment/<int:comment_pk>/remove/",
         views.comment_remove, name="find_comment_remove"),
    path("comment/<int:post_pk>/update/<int:comment_pk>",
         views.comment_update, name="find_comment_update"),
    # 검색
    #     path('search/', views.search, name="find_search"),
    # 추천수
    path('like/<int:post_id>/', views.vote_question, name="find_vote_question"),



    # 대댓글
    #     path("comment/<int:pk>/recreate/<int:comment_pk>",
    #          views.recomment_update, name="recomment_update"),

]
