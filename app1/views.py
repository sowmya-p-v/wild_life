from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from.models import*
from django.conf import settings
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    if request.method=="POST":
        username=request.POST.get('username')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        city=request.POST.get('city')
        address=request.POST.get('address')
        postal_code=request.POST.get('postal_code')
        password=request.POST.get('password')
        exists=UserRegistration.objects.filter(email=email).exists()
        if exists:
            return render(request, 'usernametaken.html')
        else:
            registration=UserRegistration(username=username,email=email,phone=phone,city=city,address=address,postal_code=postal_code,password=password)
            registration.save()
            return render(request, 'userregistrationconfirmation.html')

    return render(request, 'index.html')
    print(f"User's groups: {[group.name for group in request.user.groups.all()]}")

def userregistrationconfirmation(request):
    return render(request, 'userregistrationconfirmation.html')

def usernametaken(request):
    return render(request, 'usernametaken.html')

#login and logout
def login(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    if UserRegistration.objects.filter(email=email, password=password).exists():
        commonuserdetls = UserRegistration.objects.get(email=request.POST['email'], password=password)
        
        # Setting user to request.user after login
        request.user = commonuserdetls  # Ensure the user is set correctly
        
        # Setting session data
        request.session['uid'] = commonuserdetls.id
        request.session['uname'] = commonuserdetls.username
        request.session['phone'] = commonuserdetls.phone
        request.session['email'] = email
        request.session['cuser'] = 'cuser'

        # Redirect to inputs page after login
        return redirect('inputs')  # Use redirect instead of render
    else:
        return render(request, 'login.html', {'status': 'Invalid Username or Password'})
    
def logout(request):
    session_keys = list(request.session.keys())
    for key in session_keys:
        del request.session[key]
    return redirect(index)


def inputs(request):
    if request.user.is_authenticated:
        username = request.user.username  # Get the logged-in user's username
    else:
        username = None  # If the user is not logged in

    return render(request, 'inputs.html', {'username': username})  # Pass 'username' to template

def predictedoutputs(request):
    return render(request, 'predictedoutputs.html', {'user': request.user})


# def extrapredictions(request):
#     return render(request, 'extrapredictions.html')


from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
import numpy as np
import pandas as pd
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model

# Load the trained model and CSV files
model = load_model(r"C:\Users\Lenovo\OneDrive\Desktop\wildlife\EcoGuardian\models\cnn_model.h5")
animal_data = pd.read_csv(r"C:\Users\Lenovo\OneDrive\Desktop\wildlife\EcoGuardian\media\csv_files\Animal.csv")
effecting_factors = pd.read_csv(r"C:\Users\Lenovo\OneDrive\Desktop\wildlife\EcoGuardian\media\csv_files\Effecting_Factor.csv")
remedial_measures = pd.read_csv(r"C:\Users\Lenovo\OneDrive\Desktop\wildlife\EcoGuardian\media\csv_files\Remediation_measures.csv")
population_data = pd.read_csv(r"C:\Users\Lenovo\OneDrive\Desktop\wildlife\EcoGuardian\media\csv_files\Population_by_year.csv")
# Add other CSV file reads as required

class_labels = ['Elephant(African)', 'Amur_Leopard', 'Arctic Fox', 'Chimpanzee', 
                'Jaguars', 'Lion', 'Orangutan', 'Panda', 'Panther', 'Rhino(Black)', 'Cheetahs']

# Helper function for image prediction
def predict_image(image_path):
    image = load_img(image_path, target_size=(180, 180))  # Adjust target size
    image_array = img_to_array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    predictions = model.predict(image_array)
    predicted_class_index = np.argmax(predictions)
    predicted_class_label = class_labels[predicted_class_index]
    confidence = predictions[0][predicted_class_index] * 100
    return predicted_class_label, confidence

# Route for uploading and predicting an image

def predict(request):
    if request.method == "POST" and request.FILES['image']:
        uploaded_image = request.FILES['image']
        
        # Get the logged-in user, or set to None if not logged in
        user = request.user if request.user.is_authenticated else None
        if request.user.is_authenticated:
        # Check if the user is a researcher
            is_researcher = request.user.is_researcher()

        # Save the image and create the uploaded_image instance
        uploaded_image_instance = UploadedImage.objects.create(
        image=uploaded_image,  # Only pass the 'image' field
        )
        # is_researcher = request.user.groups.filter(name="Researchers").exists()

        # ✅ Get image path and URL
        image_path = uploaded_image_instance.image.path
        image_url = uploaded_image_instance.image.url

        # ✅ Predict image class & confidence score
        predicted_class, confidence = predict_image(image_path)
        print(f"Predicted Class: {predicted_class}")

        # ✅ Update model with actual confidence score
        uploaded_image_instance.confidence_score = confidence
        uploaded_image_instance.save()

        # Fetch additional data from CSV files based on prediction
        animal_info = animal_data[animal_data['Animal_Name'] == predicted_class].iloc[0]
        threats = effecting_factors[effecting_factors['Animal_Name'] == predicted_class].iloc[0]
        conservation = remedial_measures[remedial_measures['Animal_Name'] == predicted_class].iloc[0]

        # Prepare population trend data
        population_trend = population_data[population_data['Animal'] == predicted_class]
        population_trend['Population'] = pd.to_numeric(population_trend['Population'], errors='coerce')
        population_trend_grouped = population_trend.groupby('Year', as_index=False)['Population'].sum()

        # Generate population trend plot
        show_population_trend = not population_trend_grouped.empty
        if show_population_trend:
            population_years = population_trend_grouped['Year'].tolist()
            population_values = population_trend_grouped['Population'].tolist()

            plt.figure(figsize=(14, 10))
            plt.plot(population_years, population_values, marker='o', linestyle='-', color='b', label='Population')
            plt.title(f'Population Trend for {predicted_class}', fontsize=18)
            plt.xlabel('Year', fontsize=16)
            plt.ylabel('Population', fontsize=16)
            plt.grid(True)
            plt.legend()
            plt.tight_layout()

            # Save the plot to a BytesIO object and encode as base64
            img = BytesIO()
            plt.savefig(img, format='png', bbox_inches='tight')
            img.seek(0)
            img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
        else:
            img_base64 = None

        # Prepare details for display
        details = {
            'Animal_Name': animal_info['Animal_Name'],
            'Class': animal_info['Class'],
            'Population': animal_info['Population'],
            'Weight': animal_info['Weight'],
            'Length': animal_info['Length'],
            'Height': animal_info['Height'],
            'Habitats': animal_info['Habitats'],
            'Status': animal_info['Status'],
            'Country': animal_info['Country'],
            'Places': animal_info['Places'],
            'Threats': threats['Factor'],
            'Measures_Taken': conservation['Measure_Taken'],
        }
        request.session['details'] = details
        request.session['population_data'] = list(zip(population_years, population_values)) if show_population_trend else []
        request.session['confidence'] = f"{confidence:.2f}%"
        request.session['img_base64'] = img_base64
        print(population_data)
        
        # return redirect('extrapredictions')
        is_researcher = request.user.groups.filter(name='Researchers').exists()
        # is_researcher = request.user.is_researcher()
        

        # is_researcher = request.user.groups.filter(name='Researchers').exists()
        



        # Render 'predictedoutputs.html' and pass the data to the template
        return render(request, 'predictedoutputs.html', {
            'image_url': image_url,
            'details': details,
            'confidence': f"{confidence:.2f}%",
            'img_base64': img_base64,
            'show_population_trend': show_population_trend,
            'population_data': list(zip(population_years, population_values)) if show_population_trend else [],
            'is_researcher': is_researcher
        })

    return render(request, 'index.html')

from django.http import HttpResponseForbidden

# @login_required
def extrapredictions(request):
    if not request.user.groups.filter(name='Researchers').exists():
        return HttpResponseForbidden("You do not have permission to access this page.")

    
    # Get the data passed from the 'predict' view
    details = request.session.get('details')  # or get data from the session if needed
    population_data = request.session.get('population_data')
    confidence = request.session.get('confidence')
    img_base64 = request.session.get('img_base64')

    return render(request, 'extrapredictions.html', {
        'details': details,
        'population_data': population_data,
        'confidence': confidence,
        'img_base64': img_base64,
    })










from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import UploadedImage



# def predicted_outputs(request):
#     # Check if the user is in the 'Researchers' group
#     is_researcher = request.user.groups.filter(name='Researchers').exists()

#     return render(request, 'predictedoutputs.html', {
#         'is_researcher': is_researcher,
#     })


# @login_required
# def prediction_page(request):
#     # Check if the user is in the Researchers group
#     is_researcher = request.user.groups.filter(name="Researchers").exists()
    
    # # Debugging: Print user and groups to console
    # print(f"User: {request.user}")
    # print(f"Groups: {[group.name for group in request.user.groups.all()]}")
    # print(f"Is Researcher: {is_researcher}")

    # return render(request, 'prediction.html', {'is_researcher': is_researcher})


