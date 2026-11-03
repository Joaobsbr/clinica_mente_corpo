from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def pacientes(request):
    return render(request, 'pacientes.html')

def agenda(request):
    return render(request, 'agenda.html')

def especialidades(request):
    return render(request, 'especialidades.html')

def consultas(request):
    return render(request, 'consultas.html')

def profissionais(request):
    return render(request, 'profissionais.html')

def prontuarios(request):
    return render(request, 'prontuarios.html')

def financeiro(request):
    return render(request, 'financeiro.html')

def relatorios(request):
    return render(request, 'relatorios.html')

def configuracoes(request):
    return render(request, 'configuracoes.html')

# Create your views here.