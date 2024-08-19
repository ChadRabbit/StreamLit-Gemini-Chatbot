from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
import os
from django.views.decorators.csrf import csrf_exempt
from .models import Chat
import google.generativeai as genai
from django.utils import timezone

api_key = 'AIzaSyDj50AtvXs-fBrszDJncQkU8cXVp-8uM_Q'
genai.configure(api_key=api_key)

@csrf_exempt
def ask_gemini(message):
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    chat_session = model.start_chat(
        history=[]
    )
    response = chat_session.send_message(message)
    print(response)
    return response.text

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        message = request.POST.get('message', "")
        chats = Chat.objects.filter(user=request.user)
        chat_list = []
        if message:
            response = ask_gemini(message)
            chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
            chat.save()
        for chat in chats:
            chat_list.append({
                'message': chat.message,
                'response': chat.response,
                'created_at': chat.created_at.isoformat()  # Optional, if needed
            })
        return JsonResponse({'chats': chat_list})
    return JsonResponse({'chats': []})  # Handle GET request if needed

@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return JsonResponse({'username': username})
        else:
            error_message = 'Invalid Username or Password'
            return JsonResponse({'error_message': error_message})
    return

@csrf_exempt
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return JsonResponse({'message': 'Successfully created','username':username})
            except:
                error_message = 'Error creating account'
                return JsonResponse({'error_message': error_message})
        else:
            error_message = 'Passwords don\'t match'
            return JsonResponse({'error_message': error_message})

def logout(request):
    auth.logout(request)
    return redirect('http://localhost:8501/')
