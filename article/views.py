from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ArticlePost
import markdown
from .form import ArticlePostForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


# Create your views here.

def article_list(request):
    # 取出所有博客文章
    article_list = ArticlePost.objects.all()
    paginator = Paginator(article_list, 3)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    # 需要传递给模板的对象
    context = {
        'articles': articles,
    }
    # render函数：载入模板，并返回context对象
    return render(request, 'article/list.html', context)


def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    article.total_views += 1
    article.save(update_fields=['total_views'])

    # 将markdown语法渲染成html样式
    article.body = markdown.markdown(article.body,
                                     extensions=[
                                         'markdown.extensions.extra',
                                         'markdown.extensions.codehilite',
                                     ])

    context = {'article': article}

    return render(request, 'article/detail.html', context)


@login_required(login_url='/userprofile/login/')
def article_create(request):
    if request.method == 'POST':
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)
            new_article.save()
            return redirect("article:article_list")
        else:
            return HttpResponse("表单内容有误，请重新填写")
    else:
        article_post_form = ArticlePostForm()
        context = {'article_post_form': article_post_form}
        return render(request, 'article/create.html', context)


@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        if article.author_id != user.id:
            return HttpResponse("你没有权限删除这篇文章")
        else:
            article.delete()
            return redirect("article:article_list")
    else:
        return HttpResponse("仅允许POST请求")


@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    user = User.objects.get(id=request.user.id)
    article = ArticlePost.objects.get(id=id)
    if request.method == "POST":
        if article.author_id != user.id:
            return HttpResponse("你没有权限更改这篇文章")
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.save()
            return redirect("article:article_detail", id=id)
        else:
            return HttpResponse("表单数据有误")
    else:
        article_post_form = ArticlePostForm()
        context = {'article': article, 'article_post_form': article_post_form}
        return render(request, 'article/update.html', context)
