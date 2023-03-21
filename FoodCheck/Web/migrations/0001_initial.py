# Generated by Django 4.1.3 on 2023-03-19 11:30

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alergeno',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('imagen', models.URLField(blank=True, null=True, validators=[django.core.validators.URLValidator()])),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('nombre', models.TextField(max_length=100)),
                ('imagen', models.URLField(validators=[django.core.validators.URLValidator()])),
                ('ingredientes', models.CharField(max_length=2500)),
                ('marca', models.CharField(max_length=50)),
                ('vegano', models.BooleanField(default=True)),
                ('valoracionMedia', models.FloatField(default=0)),
                ('alergenos', models.ManyToManyField(blank=True, to='Web.alergeno')),
            ],
        ),
        migrations.CreateModel(
            name='Receta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('descripcion', models.CharField(max_length=200)),
                ('tiempoPreparacion', models.IntegerField()),
                ('publica', models.BooleanField()),
                ('productos', models.ManyToManyField(to='Web.producto')),
            ],
        ),
        migrations.CreateModel(
            name='Supermercado',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('foto', models.URLField(validators=[django.core.validators.URLValidator()])),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('telefono', models.CharField(max_length=50)),
                ('recetaDiaria', models.BooleanField(null=True)),
                ('premiumHasta', models.DateField(null=True)),
                ('es_vegano', models.BooleanField(default=False)),
                ('alergenos', models.ManyToManyField(blank=True, to='Web.alergeno')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Valoracion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('puntuacion', models.IntegerField()),
                ('comentario', models.CharField(max_length=200, null=True)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReporteAlergenos',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('alergenos', models.ManyToManyField(to='Web.alergeno')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RecetasDesbloqueadasUsuario',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('disponible', models.BooleanField()),
                ('fechaBloqueo', models.DateField()),
                ('receta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.receta')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='receta',
            name='propietario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='producto',
            name='supermercados',
            field=models.ManyToManyField(to='Web.supermercado'),
        ),
        migrations.CreateModel(
            name='ListaCompra',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('productos', models.ManyToManyField(to='Web.producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
