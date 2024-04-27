from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai
from openai import OpenAI;
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from .models import UserStory
from django.utils import timezone

user_story = UserStory()
client = OpenAI(
    api_key="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"
)

chat_completion_0 = client.chat.completions.create(
    messages = [
        {
            "role": "system", 
            "content" : "Ты мой Гейм Мастер в настольной ролевой игре под названием DnD. Ты должен предлагать мне варианты возможных действий в разных игровых ситуациях. При этом веди повествование как старый рассказчик из книг.",
        },
        {
            "role": "user",
            "content": f'Меня зовут Толик я жоский воин когда бью своих врагов кричу ныа !',
        }
    ],
    model="gpt-3.5-turbo",

)

print(chat_completion_0)

chat_response_0 = chat_completion_0.choices[0].message.content


def ask_openai(message):
    user_story.history+=message
    user_story.save
    answer = user_story.history
    response = client.chat.completions.create(
    messages = [
        {
            "role": "system", 
            "content" : "будь спокойней. не таким эксентричным. Ты мой Гейм Мастер в настольной ролевой игре под названием DnD. Используй систему DnD для проверок характеристик и навыков игрока где он будет бросать кубик 1к20, если выпало число меньше 10 происходит что-то плохое, если больше 10 то что-то хорошее. При этом каждое значение броска кубика ты должен прописывать. При этом веди повествование как старый рассказчик из книг. будь спокойнее и не торопи события а также делать более жестокий и опаснцй мир все моменты очень тшательно обыгрывай обращай внимание только на последние сообщения от пользователя учитывай что ты не союзник игроку, а наоборот пытаешся создать ему трудности и интересные ситауции Все в этом мире должны относиться ко мне с ненавистью ",
        }, 
        {
            "role": "assistant", 
            "content" : chat_response_0,
        },
        {
            "role": "assistant", 
            "content" : answer,
        },
        {
            "role": "user",
            "content": message,
        }
    ],
    model="gpt-3.5-turbo",

)   

    user_story.save
    answer = response.choices[0].message.content
    user_story.history+=answer
    print (user_story.history)
    return answer

# Create your views here.
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    user_story.user = request.user
    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)
        if user_story.history is None:  # Проверяем, является ли история пустой
            user_story.history = message
        else:
            user_story.history += '\n' + message
        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

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
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')



def logout(request):
    auth.logout(request)
    return redirect('login')