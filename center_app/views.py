# appname/views.py
from django.shortcuts import render


def main_page(request):
    return render(request, 'main.html')

def create_hashes(self,apiurl):
    hashlib= hashlib.sha256()
    m.update(b"Nobody inspects")
    m.update(b" generate new api keys")
    m.digest()
    return m.hexdigest()
    