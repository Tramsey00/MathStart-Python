"""
Постоянная карта структуры MathStart и соответствий
между рубриками WordPress и моделями Django.
"""

GRADE_STRUCTURE = [
    {
        "title": "5 класс",
        "slug": "5-klass",
        "order": 5,
        "description": "Единый курс математики для 5 класса.",
        "subjects": [
            {
                "title": "Математика",
                "slug": "matematika",
                "order": 1,
                "description": "",
            },
        ],
    },
    {
        "title": "6 класс",
        "slug": "6-klass",
        "order": 6,
        "description": "Единый курс математики для 6 класса.",
        "subjects": [
            {
                "title": "Математика",
                "slug": "matematika",
                "order": 1,
                "description": "",
            },
        ],
    },
    {
        "title": "7 класс",
        "slug": "7-klass",
        "order": 7,
        "description": "",
        "subjects": [
            {
                "title": "Алгебра",
                "slug": "algebra",
                "order": 1,
                "description": "",
            },
            {
                "title": "Геометрия",
                "slug": "geometriya",
                "order": 2,
                "description": "",
            },
            {
                "title": "Вероятность и статистика",
                "slug": "veroyatnost-i-statistika",
                "order": 3,
                "description": "",
            },
        ],
    },
    {
        "title": "8 класс",
        "slug": "8-klass",
        "order": 8,
        "description": "",
        "subjects": [
            {
                "title": "Алгебра",
                "slug": "algebra",
                "order": 1,
                "description": "",
            },
            {
                "title": "Геометрия",
                "slug": "geometriya",
                "order": 2,
                "description": "",
            },
            {
                "title": "Вероятность и статистика",
                "slug": "veroyatnost-i-statistika",
                "order": 3,
                "description": "",
            },
        ],
    },
    {
        "title": "9 класс",
        "slug": "9-klass",
        "order": 9,
        "description": "",
        "subjects": [
            {
                "title": "Алгебра",
                "slug": "algebra",
                "order": 1,
                "description": "",
            },
            {
                "title": "Геометрия",
                "slug": "geometriya",
                "order": 2,
                "description": "",
            },
            {
                "title": "Вероятность и статистика",
                "slug": "veroyatnost-i-statistika",
                "order": 3,
                "description": "",
            },
        ],
    },
]


# Ключ — term_id рубрики WordPress.
# Значение — пара (grade_slug, subject_slug).
#
# Рубрика term_id=1 «Без рубрики» намеренно не включена:
# она служебная и содержит 0 материалов.
WORDPRESS_CATEGORY_TO_SUBJECT = {
    3: ("5-klass", "matematika"),
    4: ("6-klass", "matematika"),
    59: ("7-klass", "algebra"),
    60: ("7-klass", "geometriya"),
    61: ("7-klass", "veroyatnost-i-statistika"),
    62: ("8-klass", "algebra"),
    63: ("8-klass", "geometriya"),
    64: ("8-klass", "veroyatnost-i-statistika"),
    65: ("9-klass", "algebra"),
    66: ("9-klass", "geometriya"),
    67: ("9-klass", "veroyatnost-i-statistika"),
}


EXPECTED_CATEGORY_COUNTS = {
    3: 35,
    4: 28,
    59: 36,
    60: 12,
    61: 27,
    62: 39,
    63: 12,
    64: 15,
    65: 22,
    66: 12,
    67: 12,
}

SECTION_STRUCTURE = {
    ("5-klass", "matematika"): [
        ("Натуральные числа", "naturalnye-chisla", 1),
        (
            "Разложение числа на простые множители",
            "razlozhenie-chisla-na-prostye-mnozhiteli",
            2,
        ),
        ("Обыкновенные дроби", "obyknovennye-drobi", 3),
        ("Десятичные дроби", "desyatichnye-drobi", 4),
        ("Введение в геометрию", "vvedenie-v-geometriyu", 5),
    ],

    ("6-klass", "matematika"): [
        ("Натуральные числа", "naturalnye-chisla", 1),
        (
            "Отношения, пропорции, проценты",
            "otnosheniya-proporcii-procenty",
            2,
        ),
        ("Рациональные числа", "racionalnye-chisla", 3),
        (
            "Преобразование буквенных выражений",
            "preobrazovanie-bukvennyh-vyrazhenij",
            4,
        ),
        (
            "Геометрические фигуры и тела. "
            "Симметрия на плоскости",
            "geometricheskie-figury-i-tela-simmetriya-na-ploskosti",
            5,
        ),
    ],

    ("7-klass", "algebra"): [
        ("Математические модели", "matematicheskie-modeli", 1),
        (
            "Линейная функция y = kx + b",
            "linejnaya-funkciya-y-kx-b",
            2,
        ),
        (
            "Решение систем линейных уравнений "
            "с двумя переменными",
            "reshenie-sistem-linejnyh-uravnenij-s-dvumya-peremennymi",
            3,
        ),
        (
            "Свойства степеней с натуральным показателем",
            "svojstva-stepenej-s-naturalnym-pokazatelem",
            4,
        ),
        (
            "Одночлены. Сложение и вычитание, "
            "умножение и деление одночленов",
            "odnochleny",
            5,
        ),
        (
            "Многочлены. Арифметические действия "
            "с многочленами",
            "mnogochleny",
            6,
        ),
        (
            "Разложение многочленов на множители. "
            "Способы разложения",
            "razlozhenie-mnogochlenov-na-mnozhiteli",
            7,
        ),
    ],

    ("7-klass", "geometriya"): [
        ("Основы геометрии", "osnovy-geometrii", 1),
        ("Треугольники", "treugolniki", 2),
        ("Параллельные прямые", "parallelnye-pryamye", 3),
        (
            "Соотношения в треугольнике",
            "sootnosheniya-v-treugolnike",
            4,
        ),
    ],

    ("7-klass", "veroyatnost-i-statistika"): [
        ("Представление данных", "predstavlenie-dannyh", 1),
        (
            "Описательная статистика",
            "opisatelnaya-statistika",
            2,
        ),
        (
            "Случайная изменчивость",
            "sluchajnaya-izmenchivost",
            3,
        ),
        ("Теория графов", "teoriya-grafov", 4),
        (
            "Вероятность и частота случайного события",
            "veroyatnost-i-chastota-sluchajnogo-sobytiya",
            5,
        ),
        (
            "Обобщение, систематизация знаний",
            "obobshhenie-sistematizaciya-znanij",
            6,
        ),
    ],

    ("8-klass", "algebra"): [
        (
            "Алгебраические дроби. Арифметические операции "
            "над алгебраическими дробями",
            "algebraicheskie-drobi",
            1,
        ),
        ("Действительные числа", "dejstvitelnye-chisla", 2),
        (
            "Функция y = |x|. Функция квадратного корня y = √x",
            "funkciya-modulya-i-kvadratnogo-kornya",
            3,
        ),
        ("Квадратные уравнения", "kvadratnye-uravneniya", 4),
        (
            "Квадратичная функция y = x²",
            "kvadratichnaya-funkciya-y-x2",
            5,
        ),
        (
            "Квадратичная функция y = ax². Функция y = k/x",
            "kvadratichnaya-funkciya-y-ax2-funkciya-y-k-x",
            6,
        ),
        ("Неравенства", "neravenstva", 7),
    ],

    ("8-klass", "geometriya"): [
        ("Четырёхугольники", "chetyrehugolniki", 1),
        (
            "Площади и теорема Пифагора",
            "ploshhadi-i-teorema-pifagora",
            2,
        ),
        (
            "Подобие и прямоугольные треугольники",
            "podobie-i-pryamougolnye-treugolniki",
            3,
        ),
        ("Окружность", "okruzhnost", 4),
    ],

    ("8-klass", "veroyatnost-i-statistika"): [
        (
            "Описательная статистика. Рассеивание данных",
            "opisatelnaya-statistika-rasseivanie-dannyh",
            1,
        ),
        ("Множества", "mnozhestva", 2),
        (
            "Вероятность случайного события",
            "veroyatnost-sluchajnogo-sobytiya",
            3,
        ),
        (
            "Введение в теорию графов",
            "vvedenie-v-teoriyu-grafov",
            4,
        ),
        ("Случайные события", "sluchajnye-sobytiya", 5),
        (
            "Обобщение, систематизация знаний",
            "obobshhenie-sistematizaciya-znanij",
            6,
        ),
    ],

    ("9-klass", "algebra"): [
        (
            "Неравенства и системы неравенств",
            "neravenstva-i-sistemy-neravenstv",
            1,
        ),
        (
            "Системы уравнений. Равносильные преобразования",
            "sistemy-uravnenij-ravnosilnye-preobrazovaniya",
            2,
        ),
        (
            "Числовые функции. Свойства числовых функций",
            "chislovye-funkcii",
            3,
        ),
        (
            "Числовые последовательности. Прогрессии",
            "chislovye-posledovatelnosti-progressii",
            4,
        ),
        (
            "Элементы комбинаторики, статистики "
            "и теории вероятностей",
            "elementy-kombinatoriki-statistiki-i-teorii-veroyatnostej",
            5,
        ),
    ],

    ("9-klass", "geometriya"): [
        ("Векторы", "vektory", 1),
        ("Метод координат", "metod-koordinat", 2),
        (
            "Соотношения между сторонами и углами треугольника",
            "sootnosheniya-mezhdu-storonami-i-uglami-treugolnika",
            3,
        ),
        (
            "Правильные многоугольники и окружность",
            "pravilnye-mnogougolniki-i-okruzhnost",
            4,
        ),
        (
            "Геометрические преобразования",
            "geometricheskie-preobrazovaniya",
            5,
        ),
        ("Итоговое повторение", "itogovoe-povtorenie", 6),
    ],

    ("9-klass", "veroyatnost-i-statistika"): [
        (
            "Элементы комбинаторики",
            "elementy-kombinatoriki",
            1,
        ),
        (
            "Геометрическая вероятность",
            "geometricheskaya-veroyatnost",
            2,
        ),
        ("Испытания Бернулли", "ispytaniya-bernulli", 3),
        ("Случайная величина", "sluchajnaya-velichina", 4),
        (
            "Обобщение, систематизация знаний",
            "obobshhenie-sistematizaciya-znanij",
            5,
        ),
    ],
}


EXPECTED_SECTION_TOTAL = 60


