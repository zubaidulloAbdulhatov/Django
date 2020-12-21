from django.db.models import Model
from django.shortcuts import render
from django.views.generic import DetailView, View
from .models import NoteBook, Smartphone, LatestProducts, Customer, Cart, Category
from .models import get_product_url

def index(request):
    context = NoteBook.objects.all()

    return render(request, 'index.html', {'context':context})

class ProductDetailView(DetailView):

    CT_MODEL_MODEL_CLASS = {
        'notebook': NoteBook,
        'smartphone': Smartphone
    }

    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    context_object_name = 'product'
    template_name = 'product_datail.html'
    slug_url_kwarg = 'slug'


def smartPhone(request):
    context = Smartphone.objects.all()
    return render(request, 'smartphone.html', {'context':context, 'title':'Smartphone'})

def noteBook(request):
    context = NoteBook.objects.all()
    return render(request, 'notebook.html', {'context':context, 'title':'Notebook'})

def detail_smartphone(request):
    context = Smartphone.objects.all()
    return render(request, 'detail_smartphone.html', {'context': context, 'title':'Details Smartphone'})

def detail_notebook(request):
    context = NoteBook.objects.all()
    return render(request, 'detail_notebook.html', {'context': context, 'title':'Details Notebook'})


def product_detail_n(request,id,slug):
    context = NoteBook.objects.all()
    product = NoteBook.objects.get(pk=id)
    return render(request, 'detail_notebook.html', {'context': context, 'title':'Details Notebook', 'product':product})

def product_detail_s(request, id, slug):
    context = Smartphone.objects.all()
    product = Smartphone.objects.get(pk=id)
    return render(request, 'detail_smartphone.html',{'context': context, 'title': 'Details Smartphone', 'product': product})

class CartView(View):
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user = request.user)
        cart = Cart.objects.get(owner=customer)
        context = {
            'cart': cart
        }
        return render(request, 'cart.html', context)
