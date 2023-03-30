from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect
from django import forms
import markdown2
from . import util


class SearchFrom(forms.Form):
    search_q = forms.CharField(label="", widget=forms.TextInput(attrs={"class": "form-control p-2 mb-4", "placeholder": "Search Encyclopedia", "action":"{% url 'wiki_app:search' %}", "method":"post"}))

class CreateForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={"class": "border border-primary-subtle row rounded p-2 mt-2 mb-4 ms-2", 'size':'50', "placeholder": "Search Encyclopedia", "method":"POST"}))
    content = forms.CharField(widget=forms.Textarea(attrs={"class": "border border-primary-subtle rounded row p-2 mt-2 mb-4 ms-2", "cols": "100", "rows": "20", "placeholder": "Search Encyclopedia", "action":"{% url 'wiki_app:create' %}", "method":"POST"}))

class UpdateForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={"class": "border border-primary-subtle rounded row p-2 mt-2 mb-4 ms-2", "cols": "100", "rows": "20", "placeholder": "Search Encyclopedia", "action":"{% url 'wiki_app:create' %}", "method":"POST"}))

def index(request):
    return render(request, "encyclopedia/index.html", {
    "entries": util.list_entries(),
    "search_form": SearchFrom()
    })

def title(request, title):
    content = util.get_entry(title)

    if content == None:
        return title_error(request, title)
    
    content_html = markdown2.markdown(content) 

    return render(request, "encyclopedia/title.html", {
        "title": title,
        "content": content_html,
    })

def title_error(request, title):
    return render(request, "encyclopedia/title_error.html", {
        "title": title,
    })

def search(request):
    if request.method == "POST":
        form = SearchFrom(request.POST)
        if form.is_valid():
            query = form.cleaned_data["search_q"]
            entries = util.list_entries()
            matches = [s for s in entries if query.lower() in s.lower()]
            
            if query in entries:
                return HttpResponseRedirect(f"/wiki/{query}")
            elif len(matches) > 0:
                return render(request, "encyclopedia/search_results.html", {
                    "query": query,
                    "matches": matches,
                })
            else:
                return render(request, "encyclopedia/no_search_results.html", {
                    "query": query,
                })
        else:
            print("invalid form")
            return render(request, "encyclopedia/search_error.html")
    else:
        return HttpResponseRedirect(reverse("wiki_app:index"))
    
def create(request):
    if request.method == "POST":
        create_form = CreateForm(request.POST)

        if create_form.is_valid():
            data = create_form.cleaned_data
            title = data["title"]
            if title in util.list_entries():
                return render(request, "encyclopedia/create_error.html", {
                    "status": "exists",
                    "title": title,
                })
            util.save_entry(data["title"], data["content"])
            return redirect(f"/wiki/{data['title']}")
        else:
            return render(request, "encyclopedia/create_error.html", {
                "status": "invalid"
            })

    else:
        return render(request, "encyclopedia/create.html", {
            "create_form": CreateForm()
        })

def edit(request, title):
    if request.method == "POST":
        update_form = UpdateForm(request.POST)

        if update_form.is_valid():
            data = update_form.cleaned_data
            util.save_entry(title, data["content"])
            return redirect(f"/wiki/{title}")
        else:
            return render(request, "encyclopedia/create_error.html", {
                "status": "invalid"
            })
    else:
        content = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "update_form": UpdateForm(initial={"content": content})
        })

def random(request):
    return render(request, "encyclopedia/random.html")