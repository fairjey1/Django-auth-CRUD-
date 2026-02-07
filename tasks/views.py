from urllib import request
from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm # importo el formulario de creacion de usuario que viene por defecto en django
from django.contrib.auth.models import User # importo el modelo de usuario que viene por defecto en django
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from .forms import TaskForm
from .models import Task
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'home.html') # lo mando al template signup.html

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm()}) # le paso el formulario de creacion de usuario al template
    else:
        if request.POST['password1'] == request.POST['password2']:
            try: 
                # crear el usuario
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user) # logueo al usuario creando el sessionId
                return redirect('tasks') # redirijo a la vista de tasks
            except:
                return render(request, 'signup.html', {
                    'form': UserCreationForm(), 
                    'error': 'Username already exists. Please choose another username.'
                    })
        else:
            return render(request, 'signup.html', {
                'form': UserCreationForm(), 
                'error': 'Passwords do not match.'
                })

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect('tasks')
        else:
            return render(request, 'signin.html', {
                'form': AuthenticationForm(), 
                'error': 'Invalid username or password.'
                })
        
@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {'form': TaskForm()})
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False) # creo una nueva tarea pero no la guardo en la base de datos
            new_task.user = request.user # asigno el usuario logueado a la tarea
            new_task.save() # guardo la tarea en la base de datos
            return redirect('tasks')
        except ValueError: 
            return render(request, 'create_task.html', {
                'form': TaskForm(), 
                'error': 'Error creating task. Please try again.'
                })
        
@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True) 
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user) # para que no se caiga el servidor si la tarea no existe o no pertenece al usuario
        form = TaskForm(instance=task) # para mostrar los datos de la tarea en el formulario
        return render(request, 'task_detail.html', {
            'task': task,
            'form': form
        })
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task) # para actualizar la tarea con los datos del formulario
            form.save() # guardo los cambios en la base de datos
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {
                'task': task,
                'form': form,
                'error': 'Error updating task. Please try again.'
                })
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
    return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
    return redirect('tasks')

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {'tasks': tasks})