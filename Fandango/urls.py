from django.urls import path

from Fandango.views import (
    AddPegoste, HomePage, PegosteView, Pegostes, UpdatePegoste, Pegosteadores, PegosteadorHome, RedirectSlugPegoste
)


"""
The order of the paths is no accidental.
* <username> in the end is a string, so before evaluating it, check if catalog of Pegosteadores is being call.
* If it is not the catalog of pegosteadores, then proceed to resolve other possibilities.
* Starting with <username>:
  * If no other path is provided, then it will return the "home" page of that user, which will be the last pegoste, 
    if there is any.
  * if "pegostes" comes next, then show all the pegostes created in that blog, if there is any.
  * if "pegoste" comes after <username>, then check:
    * If "add" then display the form to create a pegoste.
    * If it is an ID, then redirect to the slug of that ID.
    * if it is a slug:
        * If "update" comes after the slug, then show the update form.
        * Otherwise, just display the pegoste.  
"""

app_name = 'Fandango'
urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('pegosteadores/', Pegosteadores.as_view(), name='pegosteadores'),
    path('<username>/', PegosteadorHome.as_view(), name='pegosteador_home'),
    path('<username>/pegostes/', Pegostes.as_view(), name='pegostes_list'),
    path('<username>/pegoste/add', AddPegoste.as_view(), name='add_pegoste'),
    path('<username>/pegoste/<int:pk>/', RedirectSlugPegoste.as_view(), name='pegoste_pk'),
    path('<username>/pegoste/<slug:slug>/update', UpdatePegoste.as_view(), name='update_pegoste'),
    path('<username>/pegoste/<slug:slug>/', PegosteView.as_view(), name='pegoste'),
]
