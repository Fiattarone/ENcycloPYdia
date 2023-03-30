from django.http import JsonResponse
from .models import MyDocument
from ratelimit.exceptions import Ratelimited
from ratelimit.decorators import ratelimit


@ratelimit(key='user_or_ip', rate='100/h', block=True)
def find_document_by_word(request, word):
    try:
        if not word:
            return JsonResponse({'error': 'No search term provided.'})

        try:
            documents = MyDocument.objects.filter(word=word)
            data = [{'id': str(doc.id), 'word': doc.word, 'definition': doc.definition,
                     'synonyms': doc.synonyms, 'antonyms': doc.antonyms} for doc in documents]
            print(see_ip_and_header(request, word))
            return JsonResponse(data, safe=False)
        except MyDocument.DoesNotExist:
            return JsonResponse({'error': 'No documents found for the specified search term.'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    except Ratelimited as e:
        print(e)


def see_ip_and_header(request, word):
    ip_address = request.META.get('REMOTE_ADDR')

    header_info = request.META

    print(f'\n*********\nIP Address: {ip_address}\nSearched for word: {word}')
    print(f'\n*********\nHeader info: {header_info}\n')

    return ip_address


def ratelimited_error(request, exception):
    if isinstance(exception, Ratelimited):
        return JsonResponse({'error': 'ratelimited'}, status=429)
    return JsonResponse({'error': 'Forbidden'}, status=403)
