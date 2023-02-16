from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib.auth.decorators import login_required
from find.models import Find, FindComment, FindReComment
from .forms import FindCommentForm, FindForm
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages


def home(request):
    posts = Find.objects.order_by('-created_at')

    # 정렬 기준
    sort = request.GET.get('sort', "created_at")
    # 검색어 받기
    keyword = request.GET.get("keyword", "")
    # 검색기준 : 댓글순, 추천수, 최신순
    search_kinds = request.POST.get('search_kinds', "")

    if sort == 'view_count':
        posts = Find.objects.order_by('-view_count', '-created_at')
    elif sort == 'comment_count':
        posts = Find.objects.order_by('-comment_count', '-created_at')
        # posts = Find.objects.annotate(com_cut=Count(
        #     'comment')).order_by('-com_cut', '-created_at')
    elif sort == 'voter':
        posts = Find.objects.order_by('-voter', '-created_at')
        # posts = Find.objects.annotate(best_cnt=Count(
        #     'voter')).order_by('-best_cnt', '-created_at')
    else:
        posts = Find.objects.order_by('-created_at')

    # 검색어가 들어간 리스트만 추출
    if keyword:
        if search_kinds == 'all':
            posts = posts.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword) | Q(
                place__icontains=keyword) | Q(writer__name__icontains=keyword)).distinct()

        elif search_kinds == "title":
            posts = posts.filter(title__icontains=keyword).distinct()

        elif search_kinds == "writer":
            posts = posts.filter(writer__name__icontains=keyword).distinct()

        elif search_kinds == "content":
            posts = posts.filter(content__icontains=keyword).distinct()
        else:
            posts = posts.filter(place__icontains=keyword).distinct()

    # 현재 페이지 번호
    page = request.GET.get("page", 1)

    paginator = Paginator(posts, 4)
    list = paginator.get_page(page)

    return render(request, 'find/find_index.html', {'list': list, 'sort': sort, 'page': page, 'keyword': keyword})


# 글작성


@login_required(login_url="login")
def update(request):
    if request.method == "POST":
        form = FindForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post. writer = request.user
            post.save()
            form.save_m2m()
            return redirect("find_index")
    else:
        form = FindForm()
    return render(request, "find/find_write.html", {"form": form})

# 글 디테일


def detail(request, pk):
    post = get_object_or_404(Find, pk=pk)
    default_view_count = post.view_count
    post.view_count = default_view_count + 1
    post.save()
    return render(request, "find/find_detail.html", {"post": post})


#  글 삭제
@login_required(login_url="login")
def remove(request, pk):
    post = get_object_or_404(Find, pk=pk)
    post.delete()
    return redirect("find_index")

# 글 수정


@login_required(login_url="login")
def edit(request, pk):
    post = Find.objects.get(pk=pk)
    if request.method == "POST":
        form = FindForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.writer = request.user
            post.save()
            form.save_m2m()
            return redirect("find_index")
    else:
        form = FindForm(instance=post)
    return render(request, "find/find_edit.html", {"form": form})


# 댓글작성
@login_required(login_url="login")
def comment_create(request, pk):
    """
    댓글내용, 원본글 번호, 작성자(로그인 사용자)
    """
    post = get_object_or_404(Find, pk=pk)
    post.comment_count = post.comment_count + 1
    post.save()

    if request.method == "POST":
        comment = FindComment()
        comment.post = post
        comment.writer = request.user
        comment.contents = request.POST['contents']
        comment.save()

    return redirect("find_detail", post.pk)

# 댓글삭제


@login_required(login_url="login")
def comment_remove(request, post_pk, comment_pk):
    comment = get_object_or_404(FindComment, pk=comment_pk)
    comment.delete()

    return redirect('find_detail', post_pk)


# 댓글 수정
@login_required(login_url="login")
def comment_update(request, post_pk, comment_pk):
    comment = FindComment.objects.get(pk=comment_pk)
    if request.method == "POST":
        form = FindCommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.writer = request.user
            # comment.contents = request.POST['contents']
            comment.save()
            return redirect("find_detail", post_pk)
    else:
        form = FindForm(instance=comment)
    return render(request, "find/find_comment_update.html", {"form": form})


# 대댓글

# # 검색기능
# def search(request):
#     blogs = Find.objects.all().order_by('-id')

#     # 검색어
#     q = request.POST.get('q', "")
#     # 검색기준
#     search_kinds = request.POST.get('search_kinds', "")

#     if q:
#         if search_kinds == 'all':
#             blogs = blogs.filter(Q(title__icontains=q) | Q(content__icontains=q) | Q(
#                 place__icontains=q) | Q(writer__username__icontains=q)).distinct()

#         elif search_kinds == "title":
#             blogs = blogs.filter(title__icontains=q).distinct()

#         elif search_kinds == "writer":
#             blogs = blogs.filter(writer__username__icontains=q).distinct()

#         elif search_kinds == "content":
#             blogs = blogs.filter(content__icontains=q).distinct()
#         else:
#             blogs = blogs.filter(place__icontains=q).distinct()

#         page = request.GET.get("page", "")
#         paginator = Paginator(blogs, 9)
#         blogs = paginator.get_page(page)
#         return render(request, 'find/find_search.html', {'blogs': blogs, 'q': q, 'search_kinds': search_kinds})

#     else:
#         return render(request, 'find/find_search.html')


@login_required(login_url="login")
def vote_question(request, post_id):
    """
    질문 추천 등록 / 성공 시 detail
    질문 찾은 후 question.vote.add(로그인 사용자)
    """

    post = get_object_or_404(Find, id=post_id)

    # 자신의 글은 추천하지 못하고 타인이 쓴 글만 추천 가능
    if post.writer != request.user:
        post.voter.add(request.user)
    else:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')

    return redirect("find_detail", pk=post_id)