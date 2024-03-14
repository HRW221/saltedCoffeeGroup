import base64
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.auth import get_user
from django.contrib.auth.decorators import permission_required
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import requests

from sustainability.forms import ImageCaptureForm, PlantOfTheDayForm
from sustainability.models import Card, UsersCard

from sustainability.forms import ImageUploadForm
from sustainability.models import PlantOfTheDay


# Index view
@login_required()
def home(request):
    try:
        # Get the current plant of the day from the database
        current_plant = PlantOfTheDay.objects.get(date=timezone.now().date()).plant
    except PlantOfTheDay.DoesNotExist:
        current_plant = None
        # Render the index page
    return render(request, 'sustainability/home.html', {'current_plant': current_plant})


# View to edit the plant of the day - only for gamemasters with the permission
@login_required()
@permission_required('sustainability.add_plant_of_the_day', raise_exception=True)
def plant_of_the_day_view(request):
    # Get html form post request from the edit plant of the day page.
    if request.method == 'POST':
        form = PlantOfTheDayForm(request.POST)
        if form.is_valid():
            # Retreive the plant of the day option and save it at today's date
            plant_of_the_day = form.save(commit=False)
            plant_of_the_day.added_by = request.user
            plant_of_the_day.save()
            # Redirect back to the index
            return redirect('home')
        # If form is not valid, re-render the page
        return redirect('plant_of_the_day_view')
    else:
        # Handles the GET request, renders a form to submit the plant of the day option
        form = PlantOfTheDayForm()
        try:
            current_plant = PlantOfTheDay.objects.get(date=timezone.now().date()).plant
        except PlantOfTheDay.DoesNotExist:
            current_plant = "Not selected"
    return render(request, 'sustainability/add_plant_of_the_day.html', {'form': form, 'current_plant': current_plant})


# Account view shows the options the user has available such as viewing cards and taking a photo
@login_required()
def account_view(request):
    return render(request, 'sustainability/user.html')


# Leaderboard view shows leaderboard comparing scores of all players
@login_required()
def leaderboard_view(request):
    return render(request, 'sustainability/leaderboard.html')


# User cards view shows a list of all possible cards, the ones that are not owned by the user are greyed out
@login_required()
def users_cards_view(request):
    # Get a list of all the cards in the game
    cards = Card.objects.all()
    # Retrieve the logged in user
    current_user = request.user
    # Get a list of all the usercards the user owns
    user_cards = UsersCard.objects.filter(user_id=current_user)
    # Gets all the cards associated with a usercard belonging to the player
    user_owned_cards = [uc.card_id for uc in user_cards]

    context = {
        'cards': cards,
        'user_owned_cards': user_owned_cards,
    }
    return render(request, 'sustainability/cards.html', context=context)


# User account view shows details about the user
@login_required()
def user_account_view(request):
    # Retrieve the currently logged in user
    user = get_user(request)
    return render(request, 'sustainability/account.html', context={'user': user})


@login_required
def identify_plant_view(request):
    return render(request, 'sustainability/identify_plant_form.html')

@login_required  
def upload_plant_view(request):
    # Initialize variables to ensure they are accessible throughout the function
    plant_of_the_day_card = None
    match_message = "No Plant of the Day set for today."
    best_match = None
    first_result = None
    if request.method == 'POST':  # Checks if the request is a POST request
        form = ImageUploadForm(request.POST, request.FILES)  # Initializes the form with POST data and files
        if form.is_valid():  # Validates the form
            # Prepares the request to the PlantNet API
            api_url = 'https://my-api.plantnet.org/v2/identify/all'
            params = {
                "include-related-images": "false",
                "no-reject": "false",
                "lang": "en",
                "api-key": "2b10PCRgbtOTBNAsfjzxgiMjD"
            }
            image_file = request.FILES['image']  # Retrieves the uploaded image from the form
            files = {'images': (image_file.name, image_file, 'image/jpeg')}

            # Sends the request to the PlantNet API
            response = requests.post(api_url, params=params, files=files)

            if response.status_code == 200:  # Checks if the API request was successful
                data = response.json()  # Parses the JSON response from the API

                # Extracts relevant data from the response
                best_match = data.get('bestMatch')
                results = data.get('results', [])
                first_result = results[0] if results else None

                try:
                    today = timezone.now().date()  # Gets today's date
                    # Retrieves the PlantOfTheDay object for today
                    plant_of_the_day_card = PlantOfTheDay.objects.get(date=today).plant
                    # Gets the name of the plant of the day, converting it to lowercase for comparison
                    plant_of_the_day_name = plant_of_the_day_card.name.lower()

                    # Checks if the plant of the day's name is contained within any of the common names returned by the API
                    common_names = first_result.get('species', {}).get('commonNames', []) if first_result else []
                    is_match = any(plant_of_the_day_name in common_name.lower() for common_name in common_names)

                    # Constructs the match message based on whether a match was found
                    if is_match:
                        # Assigns the matched card to the user, creating a new UsersCard object if necessary
                        user_card, created = UsersCard.objects.get_or_create(
                            user_id=request.user,
                            card_id=plant_of_the_day_card
                        )
                        if created:
                            match_message = "Congratulations! Your plant is related to the Plant of the Day! This card has been added to your collection!"
                        else:
                            match_message = "Congratulations! Your plant is related to the Plant of the Day! However, you already have this card in your collection."
                    else:
                        match_message = "Your plant is not the Plant of the Day."
                except PlantOfTheDay.DoesNotExist:
                    match_message = "No Plant of the Day set for today."

                # Renders the result template with the collected information
                return render(request, 'sustainability/plant_identification_results.html', {
                    'best_match': best_match,
                    'result': first_result,
                    'match_message': match_message,
                    'current_plant': plant_of_the_day_card,
                })
            else:
                # Returns an error response if the API request failed
                return JsonResponse({'error': 'Failed to identify plant'}, status=response.status_code)
    else:  # Handles the case where the request is not a POST request, showing the form
        form = ImageUploadForm()
    return render(request, 'sustainability/upload_form.html', {'form': form})

@login_required  
def capture_plant_view(request):
    # Initialize variables to ensure they are accessible throughout the function
    plant_of_the_day_card = None
    match_message = "No Plant of the Day set for today."
    best_match = None
    first_result = None
    if request.method == 'POST':
        form = ImageCaptureForm(request.POST)
        if form.is_valid():
            image_data = form.cleaned_data['image_data']
            format, imgstr = image_data.split(';base64,')  # Assumes image_data is in the format: "data:image/png;base64,iVBORw0KGgo..."
            ext = format.split('/')[-1]  # Determines the extension (png, jpg, etc.)
            image_file = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            # Prepares the request to the PlantNet API
            api_url = 'https://my-api.plantnet.org/v2/identify/all'
            params = {
                "include-related-images": "false",
                "no-reject": "false",
                "lang": "en",
                "api-key": "2b10PCRgbtOTBNAsfjzxgiMjD"
            }
            files = {'images': (image_file.name, image_file, 'image/jpeg')}

            # Sends the request to the PlantNet API
            response = requests.post(api_url, params=params, files=files)

            if response.status_code == 200:  # Checks if the API request was successful
                data = response.json()  # Parses the JSON response from the API

                # Extracts relevant data from the response
                best_match = data.get('bestMatch')
                results = data.get('results', [])
                first_result = results[0] if results else None

                try:
                    today = timezone.now().date()  # Gets today's date
                    # Retrieves the PlantOfTheDay object for today
                    plant_of_the_day_card = PlantOfTheDay.objects.get(date=today).plant
                    # Gets the name of the plant of the day, converting it to lowercase for comparison
                    plant_of_the_day_name = plant_of_the_day_card.name.lower()

                    # Checks if the plant of the day's name is contained within any of the common names returned by the API
                    common_names = first_result.get('species', {}).get('commonNames', []) if first_result else []
                    is_match = any(plant_of_the_day_name in common_name.lower() for common_name in common_names)

                    # Constructs the match message based on whether a match was found
                    if is_match:
                        # Assigns the matched card to the user, creating a new UsersCard object if necessary
                        user_card, created = UsersCard.objects.get_or_create(
                            user_id=request.user,
                            card_id=plant_of_the_day_card
                        )
                        if created:
                            match_message = "Congratulations! Your plant is related to the Plant of the Day! This card has been added to your collection!"
                        else:
                            match_message = "Congratulations! Your plant is related to the Plant of the Day! However, you already have this card in your collection."
                    else:
                        match_message = "Your plant is not the Plant of the Day."
                except PlantOfTheDay.DoesNotExist:
                    match_message = "No Plant of the Day set for today."

                # Renders the result template with the collected information
                return render(request, 'sustainability/plant_identification_results.html', {
                    'best_match': best_match,
                    'result': first_result,
                    'match_message': match_message,
                    'current_plant': plant_of_the_day_card,
                })
            else:
                # Returns an error response if the API request failed
                return JsonResponse({'error': 'Failed to identify plant'}, status=response.status_code)
    else:  # Handles the case where the request is not a POST request, showing the form
        form = ImageCaptureForm()
    return render(request, 'sustainability/capture_form.html', {'form': form})
