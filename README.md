<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head>

Collective Development Job Manager
==================================

(A final project for BIONIC University Python-Web-II course by Petro Yermolenko)

Можливі дії користувачів:

* Реєстрація/вхід
* Створення проекту:
  * Самостійний проект
  * Реалізація підзадачі
  * Тестовий проект
* Створення підзадачі
* Інтегрування реалізованої підзадачі
* Завантаження збірки:
  * Робоча збірка
  * Тестова збірка
* Тестування:
  * Автопошук завдань для тестера
  * Запуск тестового завдання
  * Публікація результатів тесту
  * Спеціалізований клієнт для тестера
* Оплата/подяки:
  * Внутрішня валюта — «подяка» чи «спасибі»
  * Добровільна пожертва подяками проектові
  * Оплата за умови виконання підзадачі
  * Оплата послуг тестера
  
Важливою особливістю CoDJM є **підзадачі**. Підзадача являє собою фрагмент (чи декілька фрагментів) початкового коду,
призначених для редагування іншими розробниками. Реалізація підзадачі також може містити вкладені підзадачі, і т.д.
Реалізована підзадача піддається тестуванню (разом із основним проектом чи на тестовому проекті, спеціально створеному
для неї) і, в разі успіху, може інтегруватися в основний проект остаточно. Тестування відбувається на боці клієнта,
для чого може використовуватися спеціалізований клієнт, що в потрібний час завантажує тестову збірку, запускає тестове
завдання й публікує лог тестування (або ж усі ці дії має виконати вручну користувач-тестер).

Фрагменти коду, що виділяються в підзадачу, мають починатися з рядка, що містить текст ``:subtask ІМ’Я:``, й
закінчуватися рядком з текстом ``:endsubtask:``. ІМ'Я може бути простим (складатися лише з імені підзадачі) чи
розширеним виду ПІДЗАДАЧА/ФРАГМЕНТ — якщо один файл містить декілька фрагментів, прив'язаних до однієї підзадачі.
Таким чином, один проект може містити одну чи декілька підзадач, кожна з яких може містити один чи декілька фрагментів,
розміщених в одному чи різних файлах.

Опублікувавши проект з описаною вище розміткою, користувач автоматично створює підзадачі, якими далі він далі може
керувати: приєднати супровідну інформацію, приєднати тестовий проект, змінити статус підзадачі (неактивна (початково),
активна, виконана, анульована), встановити оплату за її реалізацію тощо. Інші користувачі можуть бачити лише активні
підзадачі даного користувача-замовника. Активну підзадачу користувач-виконавець може реалізувати: створити свій проект
на її основі й дописати свій код у вказані фрагменти. Реалізована підзадача інтегрується у проект: спершу в складі
тестової збірки, потім (коли всі тести пройдено і/або замовник підтвердив її виконання) — остаточно (зміни вносяться
в основний код проекту, підзадача отримує статус виконаної).

Структура даних
===============

``
  БД
    table user
        id
        name
        passhash
    table project
        id
        user_id
        status (project, test_project, subtask, subtask_done, subtask_cancelled)
        implementation_id
    table project_rel
        id
        project_id
        owner_id
  Файли
    users/
        <user>/
            <project>/
                file1.ext
                file2.ext
                subdir/
                    file3.txt
                    subsubdir/
                        ...``