from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index,name='home'),
    path('userregistrationconfirmation', views.userregistrationconfirmation,name='userregistrationconfirmation'),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('inputs', views.inputs,name='inputs'),
    path('predictedoutputs', views.predictedoutputs,name='predictedoutputs'),
    path('extrapredictions', views.extrapredictions,name='extrapredictions'),
    path('predict', views.predict, name='predict'),
    # path('predicted_outputs/', views.prediction_page, name='predicted_outputs'),  

]