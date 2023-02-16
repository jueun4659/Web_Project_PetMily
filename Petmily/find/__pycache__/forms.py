from django import forms
from find.models import Find, FindComment


class FindForm(forms.ModelForm):
    class Meta:
        model = Find
        fields = ["title", "place", "content", "image"]


class FindCommentForm(forms.ModelForm):
    class Meta:
        model = FindComment
        fields = ['contents']


# class ReCommentForm(forms.ModelForm):
#     class Meta:
#         model = ReComment
#         fields = ['body', 'Comment']
