from django import forms
from django.core.mail import send_mail

from blog.models import Post, Comment


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = Post
        exclude = ("author",)

    def clean(self):
        super().clean()
        send_mail(
            subject="Новая публикация!",
            message=f"Новая публикация \"{self.cleaned_data.get('title')}\"."
            f"с названием {self.cleaned_data['title']}",
            from_email="publicat_form@blogicum.not",
            recipient_list=["admin@blogicum.not"],
            fail_silently=True,
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
