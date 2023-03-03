# Generated by Django 3.0.5 on 2023-03-03 09:23

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alergeno',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Dieta',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('imagen', models.URLField(validators=[django.core.validators.URLValidator()])),
                ('ingredientes', models.CharField(max_length=200)),
                ('marca', models.CharField(max_length=50)),
                ('alergenos', models.ManyToManyField(to='Web.Alergeno')),
                ('dietas', models.ManyToManyField(to='Web.Dieta')),
            ],
        ),
        migrations.CreateModel(
            name='Receta',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('descripcion', models.CharField(max_length=200)),
                ('tiempoPreparacion', models.IntegerField()),
                ('publica', models.BooleanField()),
                ('productos', models.ManyToManyField(to='Web.Producto')),
            ],
        ),
        migrations.CreateModel(
            name='Supermercado',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('foto', models.URLField(validators=[django.core.validators.URLValidator()])),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('apellidos', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50)),
                ('telefono', models.CharField(max_length=50)),
                ('usuario', models.CharField(max_length=50)),
                ('contraseña', models.CharField(max_length=50)),
                ('recetaDiaria', models.BooleanField()),
                ('premiumHasta', models.DateField()),
                ('alergenos', models.ManyToManyField(to='Web.Alergeno')),
                ('dieta', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Web.Dieta')),
            ],
        ),
        migrations.CreateModel(
            name='Valoracion',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('puntuacion', models.IntegerField()),
                ('comentario', models.CharField(max_length=200)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.Producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.Usuario')),
            ],
        ),
        migrations.CreateModel(
            name='RecetasDesbloqueadasUsuario',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('disponible', models.BooleanField()),
                ('fechaBloqueo', models.DateField()),
                ('receta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.Receta')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.Usuario')),
            ],
        ),
        migrations.AddField(
            model_name='receta',
            name='propietario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.Usuario'),
        ),
        migrations.AddField(
            model_name='producto',
            name='supermercados',
            field=models.ManyToManyField(to='Web.Supermercado'),
        ),
        migrations.CreateModel(
            name='ListaCompra',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('productos', models.ManyToManyField(to='Web.Producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.Usuario')),
            ],
        ),
    ]
