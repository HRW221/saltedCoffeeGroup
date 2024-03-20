import base64

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core import serializers
from django.contrib import messages
from django.contrib.auth import get_user
from django.contrib.auth.decorators import permission_required
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import requests
from rest_framework.reverse import reverse

import sustainability.permissions
import sustainability.permissions
from sustainability.forms import ImageCaptureForm, PlantOfTheDayForm, LeaderboardForm, JoinLeaderboardForm, \
    ChangeDetailsForm, BecomeGameMasterForm, NonGameMLeaderboardForm
from sustainability.models import Card, UsersCard, Userprofile, Leaderboard, LeaderboardMember, Pack, GameMasterCode

from sustainability.forms import ImageUploadForm
from sustainability.models import PlantOfTheDay


# Index view
def home(request):
    try:
        # Get the current plant of the day from the database
        current_plant = PlantOfTheDay.objects.get(date=timezone.now().date()).plant
    except PlantOfTheDay.DoesNotExist:
        current_plant = None
        # Render the index page
    has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')

    return render(request, 'sustainability/home.html', {'current_plant': current_plant, 'has_permission': has_permission})


# Exeter view
def exeter_view(request):
    has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')
    return render(request, 'sustainability/exeter.html', {'has_permission': has_permission})


# View to edit the plant of the day - only for game masters with the permission
@login_required()
def plant_of_the_day_view(request):
    if not  request.user.has_perm('sustainability.add_plant_of_the_day'):
        return redirect('home')
    # Get html form post request from the edit plant of the day page.
    if request.method == 'POST':
        form = PlantOfTheDayForm(request.POST)
        if form.is_valid():
            # Retrieve the plant of the day option and save it at today's date
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
    has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')
    return render(request, 'sustainability/add_plant_of_the_day.html', {'form': form, 'current_plant': current_plant, 'has_permission': has_permission})


# Account view shows the options the user has available such as viewing cards and taking a photo
@login_required()
def account_view(request):
    has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')
    return render(request, 'sustainability/user.html', {'has_permission': has_permission})


@login_required()
def download_account(request):
    user = Userprofile.objects.get(id=request.user.id)
    groups = serializers.serialize('json', user.groups.all())
    permissions = serializers.serialize('json', user.user_permissions.all())
    return JsonResponse({
        'username': user.username,
        'first name': user.first_name,
        'last name': user.last_name,
        'email': user.email,
        'score': user.score,
        'groups': groups,
        'permissions': permissions,
    })


# Part of account view
@login_required
def delete_account(request):
    request.user.delete()
    return redirect('login')

# Leaderboard view shows leaderboard comparing scores of all players
@login_required()
def leaderboard_view(request, leaderboard_id):
    user = get_user(request)
    try:
        leaderboard = Leaderboard.objects.get(leaderboard_id=leaderboard_id)

    except Leaderboard.DoesNotExist:
        return redirect('leaderboard')
    if not LeaderboardMember.objects.filter(member_id=user,
                                            leaderboard_id=leaderboard_id).exists() and not leaderboard.is_public:
        return redirect('leaderboard')

    member_ids = LeaderboardMember.objects.filter(leaderboard_id=leaderboard_id).values_list('member_id', flat=True)
    # Fetch user profiles of members in the leaderboard, ordered by score
    leader_user_profiles = Userprofile.objects.filter(id__in=member_ids)
    user_profiles = leader_user_profiles.order_by('-score')
    user_in_leaderboard = leader_user_profiles.filter(id=request.user.id).exists()

    invite_link = request.build_absolute_uri(
        reverse('join_leaderboard') + f'?leaderboard_code={leaderboard.leaderboard_code}')
    # Pass the user profiles to the template
    has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')
    return render(request, 'sustainability/leaderboard.html',
                  {'user_profiles': user_profiles, 'leaderboard': leaderboard, 'invite_link': invite_link,
                   'user_in_leaderboard': user_in_leaderboard, 'has_permission': has_permission})


@login_required()
def leaderboard_list_view(request):
    leaderboards = LeaderboardMember.objects.filter(member_id=request.user).values_list('leaderboard_id', flat=True)
    leaderboard_list = Leaderboard.objects.filter(leaderboard_id__in=leaderboards)
    public_list = Leaderboard.objects.filter(is_public=True)
    has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')
    return render(request, 'sustainability/leaderboard_list.html',
                  {'leaderboard_list': leaderboard_list, 'public_list': public_list, 'has_permission': has_permission})


@login_required()
def create_leaderboard_view(request):
    if request.method == 'POST':
        user = request.user
        plant_of_the_day_permission, _ = sustainability.permissions.plant_of_the_day_permission
        if user.has_perm(plant_of_the_day_permission.codename):
            form = LeaderboardForm(request.POST)
            if form.is_valid():
                leaderboard_name = form.cleaned_data['leaderboard_name']
                is_public = form.cleaned_data['is_public']
                leaderboard = Leaderboard.objects.create(leaderboard_name=leaderboard_name, is_public=is_public)
                LeaderboardMember.objects.create(leaderboard_id=leaderboard, member_id=request.user)
                return redirect('leaderboard')
        else:
            form = NonGameMLeaderboardForm(request.POST)
            if form.is_valid():
                leaderboard_name = form.cleaned_data['leaderboard_name']
                is_public = False
                leaderboard = Leaderboard.objects.create(leaderboard_name=leaderboard_name, is_public=is_public)
                LeaderboardMember.objects.create(leaderboard_id=leaderboard, member_id=request.user)
                return redirect('leaderboard')
    else:
        user = request.user
        plant_of_the_day_permission, _ = sustainability.permissions.plant_of_the_day_permission
        if user.has_perm(plant_of_the_day_permission.codename):
            form = LeaderboardForm()
        else:
            form = NonGameMLeaderboardForm()
    has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')
    return render(request, 'sustainability/create_leaderboard.html', {'form': form, 'has_permission': has_permission})

@login_required()
def join_leaderboard(request):
    leaderboard_code = request.GET.get('leaderboard_code')
    initial_data = {'leaderboard_code': leaderboard_code} if leaderboard_code else None

    if request.method == 'POST':
        form = JoinLeaderboardForm(request.POST)
        if form.is_valid():
            leaderboard_code = form.cleaned_data['leaderboard_code']
            try:
                leaderboard = Leaderboard.objects.get(leaderboard_code=leaderboard_code)
            except Leaderboard.DoesNotExist:
                error_message = "Wrong code. Please enter a valid leaderboard code."
                form.add_error('leaderboard_code', error_message)
                return render(request, 'sustainability/join_leaderboard.html', {'form': form})
            LeaderboardMember.objects.create(leaderboard_id=leaderboard, member_id=request.user)
            return redirect('leaderboard_detail', leaderboard_id=leaderboard.leaderboard_id)
    else:
        form = JoinLeaderboardForm(initial=initial_data)
    has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')
    return render(request, 'sustainability/join_leaderboard.html', {'form': form, 'initial_data': initial_data, 'has_permission': has_permission})

# User cards view shows a list of all possible cards, the ones that are not owned by the user are greyed out
@login_required()
def users_cards_view(request):

    pack_list = []
    packs = Pack.objects.all()
    for pack in packs:
        pack_cards = Card.objects.filter(pack_id=pack.pack_id)
        pack_list.append(pack_cards)
    # Retrieve the logged in user
    current_user = request.user
    # Get a list of all the users cards
    user_cards = UsersCard.objects.filter(user_id=current_user)
    # Gets all the cards associated with a users card belonging to the player
    user_owned_cards = [uc.card_id for uc in user_cards]

    # Initialize variables to ensure they are accessible throughout the function
    plant_of_the_day_card = None
    match_message = None
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

                # Renders the result template with the collected information
                return render(request, 'sustainability/plant_identification_results.html', {
                    'best_match': best_match,
                    'result': first_result,
                    'match_message': match_message,
                    'current_plant': plant_of_the_day_card,
                })
            else:
                return render(request, 'sustainability/plant_identification_results.html', {
                    'best_match': best_match,
                    'result': first_result,
                    'match_message': match_message,
                    'current_plant': plant_of_the_day_card,
                })
    else:  # Handles the case where the request is not a POST request, showing the form
        form = ImageUploadForm()
    has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')
    context = {
        'packob1': packs[0],
        'pack1': pack_list[0],
        'packob2': packs[1],
        'pack2': pack_list[1],
        'packob3': packs[2],
        'pack3': pack_list[2],
        'packob4': packs[3],
        'pack4': pack_list[3],
        'packob5': packs[4],
        'pack5': pack_list[4],
        'user_owned_cards': user_owned_cards,
        'form': form,
        'has_permission': has_permission,
    }

    return render(request, 'sustainability/cards.html', context=context)


# User account view shows details about the user
@login_required()
def user_account_view(request):
    # Retrieve the currently logged in user

    if request.method == 'POST':
        form = BecomeGameMasterForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if code in GameMasterCode.objects.all().values_list('code', flat=True):
                gamemastercode = GameMasterCode.objects.get(code=code)

                if not gamemastercode.used:
                    user = request.user
                    plant_of_the_day_permission, _ = sustainability.permissions.plant_of_the_day_permission
                    if not user.has_perm(plant_of_the_day_permission.codename):
                        user.user_permissions.add(plant_of_the_day_permission)
                        gmcode = GameMasterCode.objects.get(code=code)
                        gmcode.used = True
                        gmcode.save()
                        user.save()
                        return redirect('home')
            else:
                messages.error(request, 'Invalid code.')

    user = get_user(request)
    has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')
    return render(request, 'sustainability/account.html', context={'user': user, 'has_permission': has_permission,})


#@login_required
def identify_plant_view(request):
    has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')
    return render(request, 'sustainability/cards.html', {'has_permission': has_permission,})


#@login_required
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

                today = timezone.now().date()  # Gets today's date
                # Retrieves the PlantOfTheDay object for today
                plant_of_the_day_card = PlantOfTheDay.objects.get(date=today).plant
                match_message = None

                # Renders the result template with the collected information
                has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')
                return render(request, 'sustainability/plant_identification_results.html', {
                    'best_match': best_match,
                    'result': first_result,
                    'match_message': match_message,
                    'current_plant': plant_of_the_day_card,
                    'has_permission': has_permission,
                })
            else:
                has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')
                return render(request, 'sustainability/plant_identification_results.html', {
                    'best_match': best_match,
                    'result': first_result,
                    'match_message': match_message,
                    'current_plant': plant_of_the_day_card,
                    'has_permission': has_permission,
                })
    else:  # Handles the case where the request is not a POST request, showing the form
        form = ImageUploadForm()
    has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')
    return render(request, 'sustainability/cards.html', {'form': form, 'has_permission': has_permission,})


#@login_required
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
            latitude = form.cleaned_data.get('latitude')
            longitude = form.cleaned_data.get('longitude')
            format, imgstr = image_data.split(
                ';base64,')  # Assumes image_data is in the format: "data:image/png;base64,iVBORw0KGgo..."
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
                    plant_of_the_day_name = plant_of_the_day_card.name.lower()  # Gets the name of the plant of the day, converting it to lowercase

                    # Checks if the plant of the day's name is contained within any of the common names returned by the API
                    common_names = first_result.get('species', {}).get('commonNames', []) if first_result else []
                    is_match = any(plant_of_the_day_name in common_name.lower() for common_name in common_names)
                    if latitude is not None and longitude is not None and is_within_area(latitude, longitude):
                        if is_match:
                            # Assigns the matched card to the user, creating a new UsersCard object if necessary
                            user_card, created = UsersCard.objects.get_or_create(
                                user_id=request.user,
                                card_id=plant_of_the_day_card
                            )
                            request.user.potd_bonus()
                            if created:
                                match_message = f"Congratulations! Your plant is related to the Plant of the Day ({plant_of_the_day_card.name}) and was taken in a valid location! A new card has been added to your garden. You have collected 3 bonus points :)"
                            else:
                                match_message = f"Congratulations! Your plant matches the Plant of the Day ({plant_of_the_day_card.name}) and was taken in a valid location, but you already have this card in your garden."
                        else:
                            # Identify the card from API response's common names
                            identified_card = Card.get_card_by_common_name(common_names)
                            if identified_card:
                                # If the identified card exists and belongs to a pack, add it to the user's collection
                                user_card, created = UsersCard.objects.get_or_create(
                                user_id=request.user,
                                card_id=identified_card
                                )
                                if created:
                                    match_message = "The plant you identified doesnt match the Plant of the Day. A new card has been added to your garden"
                                else:
                                    match_message = "The plant you identified is already in your garden."
                            else:
                                # Handles the case where no matching card was found or it doesn't belong to any pack
                                match_message = "No matching card in the packs or no match with Plant of the Day."
                    elif latitude is None or longitude is None:
                            match_message = "No location provided, unable to verify if the plant was taken in a valid location."
                    else:
                            match_message = "The location of the plant is invalid, unable to collect card."

                except PlantOfTheDay.DoesNotExist:
                    match_message = "There is no Plant of the Day set for today."


                # Renders the result template with the collected information
                return render(request, 'sustainability/plant_identification_results.html', {
                    'best_match': best_match,
                    'result': first_result,
                    'match_message': match_message,
                    'current_plant': plant_of_the_day_card,
                })
            else:
                return render(request, 'sustainability/plant_identification_results.html', {
                    'best_match': best_match,
                    'result': first_result,
                    'match_message': match_message,
                    'current_plant': plant_of_the_day_card,
                })
    else:  # Handles the case where the request is not a POST request, showing the form
        form = ImageCaptureForm()
    return render(request, 'sustainability/capture_form.html', {'form': form})


def is_within_area(latitude, longitude):
    # returns True if the coordinates are within the desired area
    uni_lat, uni_lon = 50.7354, -3.5339  # University of Exeter's main coordinates (approximate)
    radius = 0.01  # Approximate "radius" in degrees to consider a location valid
    return abs(float(latitude) - uni_lat) <= radius and abs(float(longitude) - uni_lon) <= radius


@login_required()
def leave_leaderboard(request, leaderboard_id):

    if request.user.is_authenticated:
        leaderboard = get_object_or_404(Leaderboard, leaderboard_id=leaderboard_id)
        if LeaderboardMember.objects.filter(leaderboard_id=leaderboard, member_id=request.user).exists():
            # Remove the user from the leaderboard members
            LeaderboardMember.objects.filter(leaderboard_id=leaderboard, member_id=request.user).delete()
            if len(LeaderboardMember.objects.filter(leaderboard_id=leaderboard)) == 0:
                leaderboard.delete()
        return redirect(
            'leaderboard')  # Redirect to the home page or any other appropriate URL after leaving the leaderboard
    return None

# view to allow users to change their details
@login_required
def change_details(request):
    if request.method == 'POST':
        form = ChangeDetailsForm(request.POST, instance=request.user)
        
        if form.is_valid():
            form.save()
            return redirect('account')
    else:
        form = ChangeDetailsForm(instance=request.user)
    has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')
    return render(request, 'sustainability/change_details.html', {'form': form, 'has_permission': has_permission,})


from django.contrib.auth.models import User


@login_required
def code_enter_view(request):
    if request.method == 'POST':
        form = BecomeGameMasterForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if code in GameMasterCode.objects.all().values_list('code', flat=True):
                gamemastercode = GameMasterCode.objects.get(code=code)

                if not gamemastercode.used:
                    user = request.user
                    plant_of_the_day_permission, _ = sustainability.permissions.plant_of_the_day_permission
                    if not user.has_perm('sustainability.add_plant_of_the_day'):
                        user.user_permissions.add(plant_of_the_day_permission)
                        gmcode = GameMasterCode.objects.get(code=code)
                        gmcode.used = True
                        gmcode.save()
                        user.save()
                        return redirect('home')
            else:
                messages.error(request, 'Invalid code.')
    has_permission = request.user.has_perm('sustainability.add_plant_of_the_day')
    return render(request, 'Sustainability/code_entry.html', {'has_permission': has_permission,})
