from django.http import JsonResponse

def hello(request):
    data = {'message': '¡Hola desde Django!'}
    return JsonResponse(data)