from django.shortcuts import render, get_object_or_404
from . models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .form import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
# Create your views here.

def post_list(request):
    post_list = Post.published.all()
    # Постраничная разбивка с 3 постами на страницу
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page')
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # Если page_number не целое число, то
        # выдать первую страницу.
        posts = paginator.page(1)
    except EmptyPage:
        # Если page_number находится вне диапозона,
        # то выдать последнюю страницу
        posts = paginator.page(paginator.num_pages)
    return render(request, 
                  'blog/post/list.html', 
                  {'posts':posts})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, 
                             
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    
    return render(request, 
                  'blog/post/detail.html', 
                  {'post':post})

def post_share(request, post_id):
    # Извлечь пост по его id
    post = get_object_or_404(Post, 
                             status=Post.Status.PUBLISHED,
                             id=post_id)
    sent = False
    if request.method == 'POST':
        # Форма была передана на обработку
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля формы успешно прошли валидацию
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommended you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n"\
                f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'console.Email-Backend', [cd['to']])
            sent = True
    else:
        form = EmailPostForm() 
    return render(request, 'blog/post/share.html', {'post':post,
                                                    'form':form,
                                                    'sent':sent})

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, 
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    comment = None
    # Комментарий был отправлен
    form = CommentForm(data = request.POST)
    if form.is_valid():
        # Создать объект класса Comment, не сохраняя его в базе данных
        comment = form.save(commit=False)
        # Назначить пост комментарию
        comment.post = post
        # Сохранить комментарий в базу данных
        comment.save()
    return render(request, 'blog/post/comment.html', 
                  {'post':post,
                   'form':form,
                   'comment':comment})