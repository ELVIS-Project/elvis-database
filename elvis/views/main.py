from django.shortcuts import render
from elvis.models import Piece
from elvis.models import Composer
from elvis.models import Movement


# Render the home page 
def home(request):
    return render(request, "home.html", {})

# LM Render the about page
def about(request):
    return render(request, "about.html", {'piece_count': Piece.objects.all().count(),
                                          'composer_count': Composer.objects.all().count(),
                                          'movement_count': Movement.objects.all().count()})

# LM Render the query page
def queries(request):
    return render(request, "query.html", {})

def contact(request):
    return render(request, "contact.html", {})
