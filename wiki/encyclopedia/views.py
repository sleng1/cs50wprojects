from django.shortcuts import render
from markdown2 import markdown
from django import forms
import random
from . import util
from django.http import HttpResponseRedirect
from django.urls import reverse

class SearchForm(forms.Form):
    search = forms.CharField(label='',
                             widget=forms.TextInput(attrs={
                                 'placeholder':'Search Encyclopedia'
                                 }))

def index(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["search"].lower() in \
                [entry.lower() for entry in util.list_entries()]:
                search_entry = form.cleaned_data["search"]
                return HttpResponseRedirect(reverse("wiki", args=[
                    search_entry]))
            entries = []
            for entry in util.list_entries():
                if form.cleaned_data["search"].lower() in entry.lower():
                    entries.append(entry)
            if entries:
                return render(request, "encyclopedia/substring.html", {
                    "entries": entries, "form": SearchForm()
                })
            else:
                search_entry = form.cleaned_data["search"]
                return HttpResponseRedirect(reverse("wiki", args=[
                    search_entry]))
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(), "form": SearchForm()
    })

def wiki(request, entry):
    if entry.lower() not in [e.lower() for e in util.list_entries()]:
        return render(request, "encyclopedia/error.html", {
            "form": SearchForm(), "error": "Page not found."
        })
    return render(request, "encyclopedia/entry.html", {
        "entry": markdown(util.get_entry(entry)), "form": SearchForm(),
        "title": entry
    }) 

def create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        body = request.POST.get("body")
        if util.get_entry(title):
            return render(request, "encyclopedia/error.html", {
                "form": SearchForm(), "error": "Page already exists."
                })
        if any([not title, not body]):
            return render(request, "encyclopedia/error.html", {
                "form": SearchForm(), "error": "Cannot create a blank page."
                })
        util.save_entry(title, body)
        return wiki(request, title)
    return render(request, "encyclopedia/new.html", {
        "form": SearchForm()
    })

def edit(request, title):
    if request.method == "POST":
        body = request.POST.get("body")
        util.save_entry(title, body)
        return HttpResponseRedirect(reverse("wiki", args=[title]))
    entry = util.get_entry(title)
    return render(request, "encyclopedia/edit.html", {
    "form": SearchForm(), "entry": entry
    })

def choose_random(request):
    return HttpResponseRedirect(reverse("wiki", args=[random.choice(
        util.list_entries())]))