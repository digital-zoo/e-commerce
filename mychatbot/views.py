# chat/views.py

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import ask_question
import json

@csrf_exempt
def chatbot_query(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question', '')
        if question:
            answer = ask_question(question)
            return JsonResponse({'answer': answer})
        return JsonResponse({'error': 'No question provided'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

# @csrf_exempt
# def chatbot_query(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             question = data.get("question", "")
#             if not question:
#                 return JsonResponse({"error": "No question provided"}, status=400)
#             answer = ask_question(question)
#             return JsonResponse({"answer": answer})
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)
#     return JsonResponse({"error": "Invalid method"}, status=405)

def chat_view(request):
    return render(request, 'chat.html')
