from django.contrib import admin
from .models import Dieta, Alergeno, Supermercado, Producto, Usuario, ListaCompra, Receta, Valoracion, RecetasDesbloqueadasUsuario

admin.site.register(Dieta)
admin.site.register(Alergeno)
admin.site.register(Supermercado)
admin.site.register(Producto)
admin.site.register(Usuario)
admin.site.register(ListaCompra)
admin.site.register(Receta)
admin.site.register(Valoracion)
admin.site.register(RecetasDesbloqueadasUsuario)