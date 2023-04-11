import datetime
import os
import requests
import time
from django.test import TestCase, Client
from django.db import connection
from Web.models import User, Producto, ListaCompra, Receta, Supermercado
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta

class ShoppingListTest(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as c, open('../datos_iniciales.sql', 'r', encoding='utf-8') as f:
            c.execute(f.read())
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='shoppinglist_testing', password='123', telefono='123456789')
        self.receta = Receta.objects.create(nombre='Receta de prueba', descripcion='Probando', propietario=self.user, publica=True, tiempoPreparacion='2 horas')
        self.receta.productos.set(Producto.objects.order_by('?')[4:7])
        self.receta.save()
    
    def login(self):
        self.client.force_login(self.user)
    
    def test_add_and_remove_product(self):
        self.login()
        product = Producto.objects.order_by('?')[0]
        
        # Adding a product
        self.client.get('/product/%s/add' % product.id)
        response = self.client.get('/shopping_list/')
        self.assertIs(response.status_code, 200, 'Logged user cannot access to the shopping list view.')
        
        # Check if the html view contains the product
        self.assertContains(response, product.nombre)
        
        # Check if the context contains the product data
        self.assertTrue('productos_agrupados_por_supermercado' in response.context.keys(), 'The view context is not correct.')
        # Market
        products_per_market = response.context['productos_agrupados_por_supermercado']
        self.assertGreater(len(set(products_per_market.keys()).intersection(set(product.supermercados.all()))), 0, 'The view context doesn\'t have the target market.')
        # Product
        self.assertTrue(product in products_per_market[product.supermercados.all()[0]], 'The view context doesn\'t contains the product')
        self.assertTrue(ListaCompra.objects.get(usuario=self.user).productos.contains(product), 'The ShoppingList model should contain the target product.')
        
        # Removing a product
        self.client.get('/product/%s/remove' % product.id)
        response = self.client.get('/shopping_list/')
        
        # Check if the html view doesn't contain the product
        self.assertNotContains(response, product.nombre)
        
        # Check if the context doesn't contain the product data
        self.assertIs(response.status_code, 200, 'Logged user cannot access to the shopping list view.')
        self.assertTrue('productos_agrupados_por_supermercado' in response.context.keys(), 'The view context is not correct.')
        products_per_market = response.context['productos_agrupados_por_supermercado']
        all_products = sum([sum(products) for products in products_per_market])
        self.assertIs(all_products, 0, 'The shopping list must be empty and it wasn\'t.')
        
        self.assertIs(ListaCompra.objects.get(usuario=self.user).productos.count(), 0, 'The ShoppingList model should be empty.')
    
    def test_add_ingredients(self):
        self.login()
        response = self.client.post('/recipe/%s/details' % self.receta.id, {'añadir-productos': ''})
        self.assertRedirects(response, '/shopping_list/')
        
        response = self.client.get('/shopping_list/')
        self.assertIs(response.status_code, 200, 'Logged user cannot access to the shopping list view.')
        
        for product in self.receta.productos.all():
            # Check if the html view contains the product
            self.assertContains(response, product.nombre)
            
            # Check if the context contains the product data
            self.assertTrue('productos_agrupados_por_supermercado' in response.context.keys(), 'The view context is not correct.')
            # Market
            products_per_market = response.context['productos_agrupados_por_supermercado']
            self.assertGreater(len(set(products_per_market.keys()).intersection(set(product.supermercados.all()))), 0, 'The view context doesn\'t have the target market.')
            # Product
            self.assertTrue(product in products_per_market[product.supermercados.all()[0]], 'The view context doesn\'t contains the product.')
            self.assertTrue(ListaCompra.objects.get(usuario=self.user).productos.contains(product), 'The ShoppingList model should contain the target product.')
        
    
    def test_availability(self):
        response = self.client.get('/shopping_list/')
        self.assertRedirects(response, '/login/?next=/shopping_list/')
        self.login()
        response = self.client.get('/shopping_list/')
        
        self.assertIs(response.status_code, 200, 'Logged user cannot access to the shopping list view.')
        
        self.assertTrue('productos_agrupados_por_supermercado' in response.context.keys(), 'The view context is not correct.')
        
        products_per_market = response.context['productos_agrupados_por_supermercado']
        all_products = sum([sum(products) for products in products_per_market])
        self.assertIs(all_products, 0, 'The shopping list must be empty and it wasn\'t')
        
        self.assertIs(ListaCompra.objects.get(usuario=self.user).productos.count(), 0, 'The ShoppingList model should be empty.')

class ListaDeLaCompraSeleniumTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        usuario= User.objects.create(username="Chema01111",
                password="pbkdf2_sha256$390000$t6AOcTYO68UNOzN7egezgY$bIoyek57DKTOQinE/ZrfrDQA6t971fFt2+Z6raILUac=",
                first_name="Albaricoque",
                last_name="Franco",
                email="cocas@gmail.com",
                telefono=23456789,
                is_active = True,
                )
        usuario.save()
        supermercado= Supermercado.objects.create(nombre="Carrefour",
                             foto="https://1000marcas.net/wp-content/uploads/2020/11/Carrefour-Logo.png"
                             )
        supermercado.save()

        producto= Producto.objects.create(id=1,
                                nombre="Garbanzos",
                                imagen="https://prod-mercadona.imgix.net/images/8a6cce24488444736497d91a7a5ec404.jpg?fit=crop&h=600&w=600",
                                ingredientes="",
                                marca="Hacendado"
                                )
        producto.supermercados.set([supermercado])
        producto.save()
        
        listacompra= ListaCompra.objects.create(usuario=usuario) 
        listacompra.productos.set([producto])       
        listacompra.save()
        
    def test_login(self):
        url='%s%s' % (self.live_server_url, '/login/')
        self.selenium.get(url)
        username_input = self.selenium.find_element(By.NAME, "username_or_email")
        username_input.send_keys('Chema01111')
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys('root')
        butom_input = self.selenium.find_element(By.XPATH, '//*[@id="logBtn"]')
        ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
        self.selenium.implicitly_wait(30)
        butom_input.click()
        producto_gamba = self.selenium.find_element(By.XPATH, "/html/body/header/nav/div/div/ul/li[2]/a")
        producto_gamba.click()
        producto_lista_garbanzos= self.selenium.find_element(By.XPATH,"/html/body/main/div[2]/div/div/div/div/p[1]")
        Garbanzos=producto_lista_garbanzos.text
        self.assertEqual(Garbanzos,"Garbanzos")
        self.selenium.quit()

class RecipesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='recipe_test', password='123', telefono='123456789')

    def login(self):
        self.client.force_login(self.user)

    def test_add_recipe(self):
        self.login()
        with open(os.path.join('Web','static','imgs','lechuga.png'),'rb') as f:
            imagen = SimpleUploadedFile(name='lechuga.png', content=f.read(), content_type='image/png')        
        
        productos=[2996514000002,3560071092801]
        response = self.client.post('/recipes/new',{'nombre':'Receta','cuerpo':'Prueba de receta','horas':'1','minutos':'0',
                                                    'segundos':'0','checkbox_publica':'si','receta_imagen':imagen,'productos':productos}, follow=True)
        receta = Receta.objects.filter(nombre='Receta',descripcion='Prueba de receta')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(receta[0].nombre, 'Receta')
        self.assertEqual(receta[0].descripcion, 'Prueba de receta')

class RecipeNegativeSeleniumTest(StaticLiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = WebDriver()
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        usuario= User.objects.create(username="recipe_test",
                password="pbkdf2_sha256$390000$t6AOcTYO68UNOzN7egezgY$bIoyek57DKTOQinE/ZrfrDQA6t971fFt2+Z6raILUac=",
                first_name="recipe_test",
                last_name="Recetas",
                email="recipe@gmail.com",
                telefono=23456789,
                is_active = True,
                )
        usuario.save()

    def test_add_recipes_negatives(self):
        url='%s%s' % (self.live_server_url, '/login/')
        self.driver.get(url)
        self.driver.find_element(By.ID, "username_or_email").click()
        self.driver.find_element(By.ID, "username_or_email").send_keys("recipe_test")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("root")
        self.driver.find_element(By.ID, "logBtn").click()
        self.driver.find_element(By.ID, "navbarDropdown").click()
        self.driver.find_element(By.LINK_TEXT, "Mis recetas").click()
        self.driver.find_element(By.LINK_TEXT, "Nueva receta").click()
        ActionChains(self.driver).scroll_by_amount(0,1000).perform()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//form/button").click()
        self.assertEqual(self.driver.current_url,self.live_server_url+'/recipes/new')

        ActionChains(self.driver).scroll_by_amount(0,-1000).perform()
        time.sleep(1)
        self.driver.find_element(By.ID, "nombre").click()
        self.driver.find_element(By.ID, "nombre").send_keys("hola")
        ActionChains(self.driver).scroll_by_amount(0,1000).perform()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//form/button").click()
        self.assertEqual(self.driver.current_url,self.live_server_url+'/recipes/new')

        ActionChains(self.driver).scroll_by_amount(0,-1000).perform()
        time.sleep(1)
        self.driver.find_element(By.ID, "cuerpo").click()
        self.driver.find_element(By.ID, "cuerpo").send_keys("hola")
        ActionChains(self.driver).scroll_by_amount(0,1000).perform()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//form/button").click()
        self.assertEqual(self.driver.current_url,self.live_server_url+'/recipes/new')

        ActionChains(self.driver).scroll_by_amount(0,-1000).perform()
        time.sleep(1)
        self.driver.find_element(By.ID, "buscadorProductosReceta").click()
        element = self.driver.find_element(By.ID, "buscadorProductosReceta")
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
        self.driver.find_element(By.ID, "buscadorProductosReceta").send_keys("pe")
        ActionChains(self.driver).scroll_by_amount(0,2000).perform()
        time.sleep(2)
        self.driver.find_element(By.XPATH, "//form/button").click()
        self.assertEqual(self.driver.current_url,self.live_server_url+'/recipes/new')

        ActionChains(self.driver).scroll_by_amount(0,1000).perform()
        time.sleep(1)
        self.driver.find_element(By.ID, "horas").click()
        self.driver.find_element(By.ID, "horas").send_keys("hola")
        time.sleep(3)
        ActionChains(self.driver).scroll_by_amount(0,2000).perform()
        self.driver.find_element(By.ID, "minutos").click()
        self.driver.find_element(By.ID, "minutos").send_keys("hola")
        time.sleep(3)
        ActionChains(self.driver).scroll_by_amount(0,2000).perform()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//form/button").click()
        self.assertEqual(self.driver.current_url,self.live_server_url+'/recipes/new')
        

class RecipeSearchTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.cursor() as c, open('../datos_iniciales.sql', 'r', encoding='utf-8') as f:
            c.execute(f.read())

    def setUp(self):
        self.URL_RECIPES = '/recipes'
        self.client = Client()
        fecha_premium = date.today() + timedelta(days=1)
        self.user = User.objects.create_user(username='user1', password='123', telefono='123456789', premiumHasta=fecha_premium)

        with open(os.path.join('Web','static','imgs','lechuga.png'),'rb') as f:
            imagen = SimpleUploadedFile(name='lechuga.png', content=f.read(), content_type='image/png')
        
            self.receta1 = Receta.objects.create(nombre='Receta1', descripcion='Probando', propietario=self.user, publica=True, tiempoPreparacion='2 horas', imagen=imagen)
            self.receta1.productos.set(Producto.objects.all()[4:7])
            self.receta1.save()

            self.receta2 = Receta.objects.create(nombre='Receta2', descripcion='Probando', propietario=self.user, publica=True, tiempoPreparacion='2 horas', imagen=imagen)
            self.receta2.productos.set(Producto.objects.all()[10:13])
            self.receta2.save()

            imagen.close()

        f.close()

    def tearDown(self):
        self.receta1.delete()
        self.receta2.delete()

    def login(self):
        self.client.force_login(self.user)

    def test_search_all_recipes(self):
        self.login()
        response = self.client.post(self.URL_RECIPES, {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Receta1')
        self.assertContains(response, 'Receta2')

        response = self.client.get(self.URL_RECIPES)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Receta1')
        self.assertContains(response, 'Receta2')

    def test_search_recipe(self):
        self.login()
        response = self.client.post(self.URL_RECIPES, {'busqueda':'Receta1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Receta1')
        self.assertNotContains(response, 'Receta2')
       
        response = self.client.post(self.URL_RECIPES, {'busqueda':'1111111'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Receta1')
        self.assertNotContains(response, 'Receta2')

    def test_search_recipe_by_product(self):
        self.login()

        producto1 = Producto.objects.all()[11]
        response = self.client.post(self.URL_RECIPES, {'productos[]':[producto1.id]})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Receta1')
        self.assertContains(response, 'Receta2')

        producto2 = Producto.objects.all()[5]
        response = self.client.post(self.URL_RECIPES, {'productos[]':[producto2.id]})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Receta1')
        self.assertNotContains(response, 'Receta2')

        response = self.client.post(self.URL_RECIPES, {'productos[]':[producto1.id, producto2.id]})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Receta1')
        self.assertNotContains(response, 'Receta2')

class Test_premium(StaticLiveServerTestCase):
     
      @classmethod
      def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)
        with connection.cursor() as c, open('../datos_iniciales.sql', 'r', encoding='utf-8') as f:
            c.execute(f.read())

      @classmethod
      def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

      def setUp(self):
        usuario= User.objects.create(username="usuarioNOpremium",
                password="pbkdf2_sha256$390000$KcrvVW94qU7dxTzlXFF22i$shL3hhA9biQBrGPIgOvLOd7hhd/4mYN1oF7FmwZUb2Q=",
                first_name="test-premium",
                last_name="kikonacho",
                email="test@gmail.com",
                telefono=123456789,
                is_active = True,
                )
        usuario.save()

        # usuario2 premium para comprobar funcionalidades
        usuario2 = User.objects.create(username="usuarioYApremium",
                password="pbkdf2_sha256$390000$KcrvVW94qU7dxTzlXFF22i$shL3hhA9biQBrGPIgOvLOd7hhd/4mYN1oF7FmwZUb2Q=",
                first_name="test-premium",
                last_name="test",
                email="test2@gmail.com",
                telefono=123456789,
                is_active = True,
                premiumHasta = datetime.date(2024,1,1)
                )
        usuario2.save()
        
        with open(os.path.join('Web','static','imgs','lechuga.png'),'rb') as f:
            imagen = SimpleUploadedFile(name='lechuga.png', content=f.read(), content_type='image/png')

        receta = Receta.objects.create(nombre='Receta para desbloqueo y añadido de productos',
                                      descripcion='Probando',
                                      propietario=usuario,
                                      publica=True,
                                      imagen=imagen,
                                      tiempoPreparacion='2 horas')
        receta.productos.set(Producto.objects.order_by('?')[4:7])
        receta.save()

        receta = Receta.objects.create(nombre='Receta para desbloqueo > 1',
                                      descripcion='Probando',
                                      propietario=usuario,
                                      publica=True,
                                      imagen=imagen,
                                      tiempoPreparacion='2 horas')
        receta.productos.set(Producto.objects.order_by('?')[4:7])
        receta.save()

      def tearDown(self):
        Receta.objects.all().delete()
        User.objects.all().delete()
        

      def test_become_premium(self):
            url='%s%s' % (self.live_server_url, '/login/')
            self.selenium.get(url)
            self.selenium.set_window_size(1936, 1096)
            username_input = self.selenium.find_element(By.NAME, "username_or_email")
            username_input.send_keys('usuarioNOpremium')
            password_input = self.selenium.find_element(By.NAME, "password")
            password_input.send_keys('callatebobo')
            butom_input = self.selenium.find_element(By.XPATH, '//*[@id="logBtn"]')
            ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
            self.selenium.implicitly_wait(30)
            butom_input.click()
            self.selenium.find_element(By.LINK_TEXT, "Plan premium").click()
            self.selenium.find_element(By.LINK_TEXT, "Hacerse premium!").click()
            self.selenium.find_element(By.ID, "email").click()
            self.selenium.find_element(By.ID, "email").send_keys("test@gmail.com")
            self.selenium.find_element(By.ID, "cardNumber").click()
            self.selenium.find_element(By.ID, "cardNumber").send_keys("4242 4242 4242 4242")
            self.selenium.find_element(By.ID, "cardExpiry").click()
            self.selenium.find_element(By.ID, "cardCvc").click()
            self.selenium.find_element(By.ID, "cardCvc").send_keys("424")
            self.selenium.find_element(By.ID, "cardExpiry").click()
            self.selenium.find_element(By.ID, "cardExpiry").send_keys("01 / 42")
            self.selenium.find_element(By.ID, "billingName").click()
            self.selenium.find_element(By.ID, "cardExpiry").click()
            self.selenium.find_element(By.ID, "billingName").click()
            self.selenium.find_element(By.ID, "billingName").send_keys("Prueba")
            self.selenium.find_element(By.CSS_SELECTOR, ".SubmitButton-IconContainer").click()
            wait = WebDriverWait(self.selenium,10)
            wait.until(EC.url_contains('/payment_completed'))
            session_id = self.selenium.current_url.split("=")[1]
            url='%s%s' % (self.live_server_url, '/payment_completed?session_id=' + str(session_id))
            self.selenium.get(url)

            usuario = User.objects.get(username='usuarioNOpremium')
            self.assertIsNotNone(usuario.subscription)

      def test_recetaPrivadaPremium(self):

            url='%s%s' % (self.live_server_url, '/login/')
            self.selenium.get(url)
            self.selenium.set_window_size(1936, 1096)
            username_input = self.selenium.find_element(By.NAME, "username_or_email")
            username_input.send_keys('usuarioYApremium')
            password_input = self.selenium.find_element(By.NAME, "password")
            password_input.send_keys('callatebobo')
            butom_input = self.selenium.find_element(By.XPATH, '//*[@id="logBtn"]')
            ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
            self.selenium.implicitly_wait(30)
            butom_input.click()

            #Creando una receta privada 

            # ruta necesaria para añadir imagen a receta
            rutaRelativa = "Web\\static\\imgs\\lechuga.png"
            rutaAbsoluta = os.path.abspath(rutaRelativa)
            print(rutaAbsoluta)

            self.selenium.find_element(By.ID, "navbarDropdown").click()
            self.selenium.find_element(By.LINK_TEXT, "Mis recetas").click()
            self.selenium.find_element(By.LINK_TEXT, "Nueva receta").click()
            self.selenium.find_element(By.ID, "nombre").click()
            self.selenium.find_element(By.ID, "nombre").send_keys("test")
            self.selenium.find_element(By.ID, "cuerpo").click()
            self.selenium.find_element(By.ID, "cuerpo").send_keys("test")
            self.selenium.find_element(By.ID, "buscadorProductosReceta").click()
            self.selenium.find_element(By.ID, "buscadorProductosReceta").send_keys("Queso")
            time.sleep(0.5)
            self.selenium.find_element(By.LINK_TEXT, "Queso semicurado mezcla Entrepinares lonchas").click()
            self.selenium.find_element(By.LINK_TEXT, "Queso tierno mezcla Entrepinares lonchas").click()
            self.selenium.find_element(By.ID, "receta_imagen").send_keys(rutaAbsoluta)
            ActionChains(self.selenium).scroll_by_amount(0,2000).perform()
            time.sleep(1)
            self.selenium.find_element(By.ID, "horas").click()
            self.selenium.find_element(By.ID, "horas").send_keys("05")
            self.selenium.find_element(By.ID, "minutos").click()
            self.selenium.find_element(By.ID, "minutos").send_keys("05")
            self.selenium.find_element(By.ID, "segundos").click()
            self.selenium.find_element(By.ID, "segundos").send_keys("05")
            self.selenium.find_element(By.ID, "checkbox_publica").click()
            self.selenium.find_element(By.ID, "filter-form").click()
            self.selenium.find_element(By.ID, "boton-busqueda").click()

            #Comprobamos la redirección a my_recipes

            redireccionOK = self.selenium.find_element(By.LINK_TEXT, "Nueva receta")
            self.assertIsNotNone(redireccionOK)

            receta = Receta.objects.latest("id")
            self.assertFalse(receta.publica)

      def test_recetaPrivadaNoPremium(self):

            url='%s%s' % (self.live_server_url, '/login/')
            self.selenium.get(url)
            self.selenium.set_window_size(1936, 1096)
            username_input = self.selenium.find_element(By.NAME, "username_or_email")
            username_input.send_keys('usuarioNOpremium')
            password_input = self.selenium.find_element(By.NAME, "password")
            password_input.send_keys('callatebobo')
            butom_input = self.selenium.find_element(By.XPATH, '//*[@id="logBtn"]')
            ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
            self.selenium.implicitly_wait(5)
            butom_input.click()

            #Creando una receta privada 

            # ruta necesaria para añadir imagen a receta
            rutaRelativa = "Web\\static\\imgs\\lechuga.png"
            rutaAbsoluta = os.path.abspath(rutaRelativa)
            print(rutaAbsoluta)

            self.selenium.find_element(By.ID, "navbarDropdown").click()
            self.selenium.find_element(By.LINK_TEXT, "Mis recetas").click()
            self.selenium.find_element(By.LINK_TEXT, "Nueva receta").click()
            self.selenium.find_element(By.ID, "nombre").click()
            self.selenium.find_element(By.ID, "nombre").send_keys("test")
            self.selenium.find_element(By.ID, "cuerpo").click()
            self.selenium.find_element(By.ID, "cuerpo").send_keys("test")
            self.selenium.find_element(By.ID, "buscadorProductosReceta").click()
            self.selenium.find_element(By.ID, "buscadorProductosReceta").send_keys("Queso")
            ActionChains(self.selenium).scroll_by_amount(0,100).perform()
            time.sleep(0.5)
            self.selenium.find_element(By.LINK_TEXT, "Queso semicurado mezcla Entrepinares lonchas").click()
            self.selenium.find_element(By.LINK_TEXT, "Queso tierno mezcla Entrepinares lonchas").click()
            self.selenium.find_element(By.ID, "receta_imagen").send_keys(rutaAbsoluta)
            ActionChains(self.selenium).scroll_by_amount(0,2000).perform()
            time.sleep(1)
            self.selenium.find_element(By.ID, "horas").click()
            self.selenium.find_element(By.ID, "horas").send_keys("01")
            self.selenium.find_element(By.ID, "minutos").click()
            self.selenium.find_element(By.ID, "minutos").send_keys("01")
            self.selenium.find_element(By.ID, "segundos").click()
            self.selenium.find_element(By.ID, "segundos").send_keys("01")
            self.selenium.find_element(By.ID, "filter-form").click()
            self.selenium.find_element(By.ID, "boton-busqueda").click()

            #Comprobamos la redirección a my_recipes

            redireccionOK = self.selenium.find_element(By.LINK_TEXT, "Nueva receta")
            self.assertIsNotNone(redireccionOK)

            receta = Receta.objects.latest("id")
            self.assertFalse(receta.publica)

      def test_accesoDiscoverPremium(self):

            url='%s%s' % (self.live_server_url, '/login/')
            self.selenium.get(url)
            self.selenium.set_window_size(1936, 1096)
            username_input = self.selenium.find_element(By.NAME, "username_or_email")
            username_input.send_keys('usuarioYApremium')
            password_input = self.selenium.find_element(By.NAME, "password")
            password_input.send_keys('callatebobo')
            butom_input = self.selenium.find_element(By.XPATH, '//*[@id="logBtn"]')
            ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
            self.selenium.implicitly_wait(30)
            butom_input.click()

            # Accede al sistema de recomendación

            self.selenium.find_element(By.LINK_TEXT, "Discover").click()
            titulo_visible = self.selenium.find_element(By.CLASS_NAME, "title")
            self.assertIsNotNone(titulo_visible)

      def test_accesoDiscoverNoPremium(self):

            url='%s%s' % (self.live_server_url, '/login/')
            self.selenium.get(url)
            self.selenium.set_window_size(1936, 1096)
            username_input = self.selenium.find_element(By.NAME, "username_or_email")
            username_input.send_keys('usuarioYApremium')
            password_input = self.selenium.find_element(By.NAME, "password")
            password_input.send_keys('callatebobo')
            butom_input = self.selenium.find_element(By.XPATH, '//*[@id="logBtn"]')
            ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
            self.selenium.implicitly_wait(30)
            butom_input.click()
            discover = self.selenium.find_element(By.LINK_TEXT, "Discover")
            self.assertIsNotNone(discover)

      def test_desbloquearReceta_anadirProductos(self):

            url='%s%s' % (self.live_server_url, '/login/')
            self.selenium.get(url)
            self.selenium.set_window_size(1936, 1096)
            username_input = self.selenium.find_element(By.NAME, "username_or_email")
            username_input.send_keys('usuarioYApremium')
            password_input = self.selenium.find_element(By.NAME, "password")
            password_input.send_keys('callatebobo')
            butom_input = self.selenium.find_element(By.XPATH, '//*[@id="logBtn"]')
            ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
            self.selenium.implicitly_wait(30)
            butom_input.click()

            self.selenium.find_element(By.ID, "navbarDropdown").click()
            self.selenium.find_element(By.LINK_TEXT, "Todas las recetas").click()
            self.selenium.find_element(By.XPATH, '//*[@id="row-details"]/div/div/a/img').click() #receta 1

            compruebaRecetaBloqueada = self.selenium.find_element(By.ID, "boton-desbloqueo")
            self.assertIsNotNone(compruebaRecetaBloqueada)

            # Desbloqueamos
            ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
            time.sleep(1)
            self.selenium.find_element(By.ID, "boton-desbloqueo").click()

            compruebaRecetaDesbloqueada = self.selenium.find_element(By.ID, "boton-productos-lista")
            self.assertIsNotNone(compruebaRecetaDesbloqueada)

            # Añadimos sus productos a la lista de compra
            ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
            time.sleep(1)
            self.selenium.find_element(By.ID, "boton-productos-lista").click()

            redireccionOK = self.selenium.find_element(By.XPATH, "/html/body/main/div[2]/div/h1")
            self.assertIsNotNone(redireccionOK)

            # comprobamos que el user premium puede desbloquear más de una receta:

            self.selenium.find_element(By.ID, "navbarDropdown").click()
            self.selenium.find_element(By.LINK_TEXT, "Todas las recetas").click()
            self.selenium.find_element(By.XPATH, '//*[@id="row-details"]/div[2]/div/a/img').click() # receta 2
            ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
            time.sleep(1)
            self.selenium.find_element(By.ID, "boton-desbloqueo").click()
            compruebaRecetaDesbloqueada2 = self.selenium.find_element(By.ID, "boton-productos-lista")
            self.assertIsNotNone(compruebaRecetaDesbloqueada2)


      def test_desbloquearReceta_anadirProductosNoPremium(self):

            url='%s%s' % (self.live_server_url, '/login/')
            self.selenium.get(url)
            self.selenium.set_window_size(1936, 1096)
            username_input = self.selenium.find_element(By.NAME, "username_or_email")
            username_input.send_keys('usuarioYApremium')
            password_input = self.selenium.find_element(By.NAME, "password")
            password_input.send_keys('callatebobo')
            butom_input = self.selenium.find_element(By.XPATH, '//*[@id="logBtn"]')
            ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
            self.selenium.implicitly_wait(5)
            butom_input.click()

            self.selenium.find_element(By.ID, "navbarDropdown").click()
            self.selenium.find_element(By.LINK_TEXT, "Todas las recetas").click()
            self.selenium.find_element(By.XPATH, '//*[@id="row-details"]/div/div/a/img').click() #receta 1

            compruebaRecetaBloqueada = self.selenium.find_element(By.ID, "boton-desbloqueo")
            self.assertIsNotNone(compruebaRecetaBloqueada)

            # Desbloqueamos

            ActionChains(self.selenium).scroll_by_amount(0,1000).perform()
            time.sleep(1)
            self.selenium.find_element(By.ID, "boton-desbloqueo").click()

            compruebaRecetaDesbloqueada = self.selenium.find_element(By.ID, "boton-productos-lista")
            self.assertIsNotNone(compruebaRecetaDesbloqueada)

            self.selenium.find_element(By.ID, "navbarDropdown").click()
            self.selenium.find_element(By.LINK_TEXT, "Todas las recetas").click()
            self.selenium.find_element(By.XPATH, '//*[@id="row-details"]/div[2]/div/a/img').click() # receta 2
            usuario = User.objects.latest("id")
            self.assertTrue(usuario.recetaDiaria)
