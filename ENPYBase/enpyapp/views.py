from django.http import JsonResponse
from .models import MyDocument


def find_document_by_word(request, word):
    documents = MyDocument.objects.filter(word=word)
    data = [{'id': str(doc.id), 'word': doc.word, 'definition': doc.definition,
             'synonyms': doc.synonyms, 'antonyms': doc.antonyms} for doc in documents]
    return JsonResponse(data, safe=False)

