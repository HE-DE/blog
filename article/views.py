from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import ArticlePost
import markdown
from .form import ArticlePostForm
from django.contrib.auth.models import User


# Create your views here.

def article_list(request):
    # 取出所有博客文章
    articles = ArticlePost.objects.all()
    # 需要传递给模板的对象
    context = {
        'articles': articles,
    }
    # render函数：载入模板，并返回context对象
    return render(request, 'article/list.html', context)


def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)

    # 将markdown语法渲染成html样式
    article.body = markdown.markdown(article.body,
                                     extensions=[
                                         'markdown.extensions.extra',
                                         'markdown.extensions.codehilite',
                                     ])

    context = {'article': article}

    return render(request, 'article/detail.html', context)

def article_create(request):
    if request.method=='POST':
        article_post_form=ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            new_article=article_post_form.save(commit=False)
            new_article.author=User.objects.get(id=1)
            new_article.save()
            return redirect("article:article_list")
        else:
            return HttpResponse("表单内容有误，请重新填写")
    else:
        article_post_form=ArticlePostForm()
        context={'article_post_form':article_post_form}
        return render(request,'article/create.html',context)