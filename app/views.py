from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import PostForm
from .models import Post, HashTag


def home(request):
    return render(request, 'home.html', {})


class PostCreate(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'create_post.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(PostCreate, self).get_form_kwargs()
        data = self.request.POST.copy()
        hashtags = data.getlist('hashtags')
        hashtags = [hashtag for hashtag in hashtags if hashtag != '']
        if len(hashtags) > 0:
            hashtags = [str(HashTag.objects.get_or_create(name=hashtag)[0].pk) for hashtag in hashtags[0].split(',')]
        data.setlist('hashtags', hashtags)
        kwargs['data'] = data
        return kwargs
