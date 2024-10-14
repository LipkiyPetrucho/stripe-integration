## Stripe Django Проект
### Стек технологий:
 - ![alt text](https://img.shields.io/badge/Python-3.12-grey?style=plastic&logo=python&logoColor=white&labelColor=%233776AB)

 - ![alt text](https://img.shields.io/badge/Django-5.1-grey?style=plastic&logo=django&logoColor=white&labelColor=%23092E20)

 - ![alt text](https://img.shields.io/badge/Docker-v25.0.3-grey?style=plastic&logo=docker&logoColor=white&labelColor=2496ED)

 - ![alt text](https://img.shields.io/badge/Redis-5.1.1-grey?style=plastic&logo=redis&logoColor=white&labelColor=DC382D)
### Описание проекта
Это проект для создания интернет-магазина с использованием Django и Stripe API. Приложение поддерживает управление товарами, оформление заказов и интеграцию с системой платежей Stripe.

***

### Функционал
#### Модели Django:
- Item: Товар с полями name, description, price, currency.
- Order: Заказ, состоящий из нескольких товаров.
- Coupon и Tax: Применение скидок и налогов при оформлении заказа.

#### Интеграция с Stripe:
- Получение Stripe Session ID для оплаты конкретного товара через /buy/{id}.
- Перенаправление на страницу оплаты Stripe с помощью JavaScript.
- Поддержка как Stripe Sessions, так и Payment Intents.

#### Дополнительные возможности:
- Использование переменных окружения для хранения ключей.
- Поддержка Docker для локального запуска.
- Административная панель для управления товарами и заказами.
- Поддержка нескольких валют (RUB, USD) с использованием нескольких Stripe Keypairs.

***

### API Endpoints
-  #### GET /buy/{id}:
  Возвращает Stripe Session ID для оплаты товара.
- #### GET /item/{id}:
  Отображает HTML-страницу с информацией о товаре и кнопкой для оплаты.

***

### Установка и запуск
#### Необходимые условия
Убедитесь, что в вашей системе установлено следующее:

- Docker
- Docker Compose
- Python 12.4+
- Аккаунт Stripe (для ключей API)

### Локальный запуск с Docker

<details>
<summary>Для запуска через Docker необходимо:</summary>

1.Клонируйте репозиторий и перейдите в каталог проекта:
```bash
git clone https://github.com/LipkiyPetrucho/stripe-integration.git
cd stripe-django-project
```
2.Прописать переменные окружения в файле `.env.sample`. Имя файла необходимо заменить на .env:

```dotenv
SECRET_KEY='Секретный ключ Django'
DEBUG='True/False', например: True
STRIPE_SECRET_KEY=ваш_stripe_secret_key'
STRIPE_PUBLISHABLE_KEY=ваш_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

3.Соберите и запустите контейнеры Docker
```bash
docker-compose up --build
```

### Миграция базы данных
Внутри контейнера Docker выполните следующие действия, чтобы применить миграцию:
```bash
  docker-compose exec web python manage.py migrate
```

### Доступ администратора
Чтобы создать пользователя-администратора для доступа к панели администратора Django:
```bash
docker-compose exec web python manage.py createsuperuser
```
- ввести логин, например admin
- почту(опционально)
- ввести пароль, например admin

 зайти на http://127.0.0.1:8000/admin/ либо http://localhost:8000/admin/
- login: admin
- password: admin

***

### Для завершения работы необходимо:

 - Нажать комбинацию клавиш `CTRL + C` в окне терминала

***

### Запуск приложения
Как только контейнеры будут запущены, вы сможете получить доступ к приложению:
- Django Admin: http://localhost:8000/admin
- API and Web Interface: http://localhost:8000

### Тестирование потоков платежей
Вы можете протестировать платежи, используя тестовый режим Stripe.
Создайте тестовые `товары` в панели администратора,
а затем посетите страницу `/item/{id}`, чтобы инициировать сеанс оформления заказа.

### Docker Setup
Проект включает в себя `Dockerfile` и `docker-compose.yml` для контейнерного развертывания:
- **Веб-контейнер**: Запускает приложение Django.
- **Redis**: Используется для кэширования.

### Дополнительные возможности
- **Купоны и скидки**: Применяйте скидки, основанные на процентах, используя модель Coupon.
- **Налоги**: Добавляйте налоги к заказам на основе предопределенных ставок.
- **Поддержка мультивалютности**: Цены можно устанавливать в рублях или долларах США с автоматической конвертацией валют при подсчете общей суммы заказа.

### Использование
- **Создание элементов**: Используйте панель администратора для создания и управления объектами `товаров`.
- **Оформление заказа**: Пользователи могут просматривать детали товаров и переходить к оплате с помощью страницы оформления заказа Stripe.
- **Создание заказа**: Объедините несколько товаров в заказ и перейдите к оплате общей суммы.

</details>

***

### Лицензия
Проект распространяется по лицензии MIT.

***

<details>
<summary><b>Connect with me:</b></summary>
   <p align="left">
       <a href="mailto:pafos.light@gmail.com"><img src="https://img.shields.io/badge/gmail-%23EA4335.svg?style=plastic&logo=gmail&logoColor=white" alt="Gmail"/></a>
       <a href="https://t.me/petr_lip"><img src="https://img.shields.io/badge/telegram-blue?style=plastic&logo=telegram&logoColor=white" alt="Telegram"/></a>
   </p>
</details>