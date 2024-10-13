## Stripe Django Проект
### Стек технологий:
 - ![alt text](https://img.shields.io/badge/Python-3.12-grey?style=plastic&logo=python&logoColor=white&labelColor=%233776AB)

 - ![alt text](https://img.shields.io/badge/Django-5.1-grey?style=plastic&logo=django&logoColor=white&labelColor=%23092E20)

 - ![alt text](https://img.shields.io/badge/Docker-v25.0.3-grey?style=plastic&logo=docker&logoColor=white&labelColor=2496ED)
### Описание проекта
Это проект для создания интернет-магазина с использованием Django и Stripe API. Приложение поддерживает управление товарами, оформление заказов и интеграцию с системой платежей Stripe.

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

### API
- GET /buy/{id}: Возвращает Stripe Session ID для оплаты товара.
- GET /item/{id}: Отображает HTML-страницу с информацией о товаре и кнопкой для оплаты.

### Локальный запуск с Docker

<details>
<summary>Для запуска через Docker необходимо:</summary>

1.Клонируйте репозиторий и перейдите в каталог проекта:
```bash
git clone https://github.com/LipkiyPetrucho/stripe-integration.git
cd stripe-django-project
```
2.Создайте файл .env с переменными окружения:
```dotenv
SECRET_KEY=ваш_секретный_ключ
STRIPE_SECRET_KEY=ваш_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=ваш_stripe_publishable_key
```
3.Соберите и запустите контейнеры Docker
```bash
docker-compose up --build
```
</details>
Лицензия
Проект распространяется по лицензии MIT.