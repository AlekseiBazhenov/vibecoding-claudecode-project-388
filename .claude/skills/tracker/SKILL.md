---
name: tracker
description: >-
  Обходит зашитый список URL товаров и собирает единую таблицу цен. Применять,
  когда пользователь просит отследить/собрать цены сразу по нескольким товарам,
  сделать сводку или таблицу цен по списку ссылок магазина «Полюс» (polus73.ru).
  Для каждого URL переиспользует навык extract-price и складывает результаты в
  одну таблицу прогона (по строке на товар).
---

# Tracker

Навык обходит **зашитый список URL** товаров и собирает **единую таблицу цен** за
один прогон. Логику извлечения цены навык **не дублирует** — он переиспользует
готовый навык [`extract-price`](../extract-price/SKILL.md).

## Контракт

**Вход:** нет (список URL зашит в тело этого навыка, см. ниже).

**Выход:** таблица прогона — одна строка на товар. Колонки:

| Колонка              | Значение |
|----------------------|----------|
| `url`                | Ссылка на страницу товара. |
| `name`               | Название товара. |
| `regular_price`      | Обычная цена (число). |
| `sale_price_regular` | Цена без скидки (перечёркнутая) или `null`, если скидки нет. |
| `is_available`       | В наличии. |

Отсутствующее значение поля → `"-"` (как задаёт `extract-price`).

## Список отслеживаемых URL

1. https://polus73.ru/article/49432/avtoholodilnik_biryusa_ns_12p1_belyy
2. https://polus73.ru/article/49433/avtoholodilnik_biryusa_ns_12p2_zelenyy
3. https://polus73.ru/article/49434/avtoholodilnik_biryusa_ns_18p1_belyy
4. https://polus73.ru/article/49435/avtoholodilnik_biryusa_ns_18p2_zelenyy
5. https://polus73.ru/article/49436/avtoholodilnik_biryusa_ns_18p5_temno_siniy
6. https://polus73.ru/article/49437/avtoholodilnik_biryusa_ns_22p3_bordovyy
7. https://polus73.ru/article/49621/avtoholodilnik_biryusa_ns_22p5_temno_siniy
8. https://polus73.ru/article/49429/avtoholodilnik_biryusa_ns_24g1_chernyy
9. https://polus73.ru/article/51357/avtoholodilnik_biryusa_ns_30p7_oranzhevo_chernyy
10. https://polus73.ru/article/51360/avtoholodilnik_biryusa_ns_38p7_oranzhevo_chernyy

## Главный сценарий

1. **Взять список URL** из раздела «Список отслеживаемых URL» выше.
2. **Для каждого URL** по очереди вызвать навык `extract-price`, передав ему этот
   URL. Навык вернёт объект цены с полями `name`, `regular_price`,
   `sale_price_regular`, `is_available`.
   - Не извлекай цены самостоятельно и не копируй логику `extract-price` —
     переиспользуй сам навык.
3. **Собрать результаты в единую таблицу прогона:** одна строка на товар; в
   строке — `url` и все поля, полученные от `extract-price`
   (`name`, `regular_price`, `sale_price_regular`, `is_available`).
4. **Вывести таблицу** пользователю. Порядок строк соответствует порядку URL в
   списке.
5. **Сохранить прогон в репозиторий `tracker-data`** (см. «Схема хранения»
   ниже) — записать таблицу как файл `YYYY-MM-DD.json` через GitHub MCP.

## Схема хранения

- **Один прогон — один файл.** Имя файла — дата прогона в формате
  `YYYY-MM-DD.json` (например, `2026-07-13.json`).
- Файл лежит в **корне репозитория `tracker-data`**.
- Внутри файла — **таблица прогона в формате JSON**: массив объектов, по одному
  на товар, с полями `url`, `name`, `regular_price`, `sale_price_regular`,
  `is_available`.

Пример содержимого `2026-07-13.json`:

```json
[
  {
    "url": "https://polus73.ru/article/49432/avtoholodilnik_biryusa_ns_12p1_belyy",
    "name": "Автохолодильник Бирюса НС-12P1 Белый",
    "regular_price": 14695,
    "sale_price_regular": null,
    "is_available": true
  }
]
```

## Коммит через GitHub MCP

После сборки таблицы записать её в репозиторий `tracker-data` **через GitHub
MCP** — инструментом создания/обновления файла (`create_or_update_file`).

- Путь файла в репозитории: `YYYY-MM-DD.json` (в корне).
- Содержимое: JSON-таблица прогона (см. «Схема хранения»).
- Сообщение коммита: например, `tracker run YYYY-MM-DD`.
- **Запись файла через MCP — это сразу отдельный коммит**, без локального
  `git clone` и `git push`. Не клонировать репозиторий и не пушить руками —
  использовать только MCP-инструмент.
- Если файл с такой датой уже существует (повторный прогон за день) — обновить
  его (передать актуальный `sha` существующего файла), перезаписав содержимое.

## Замечания

- Если для какого-то URL `extract-price` не смог найти значение — в
  соответствующую ячейку ставится `"-"`, а отсутствие скидки — `null` в
  колонке `sale_price_regular`.
- Чтобы добавить или убрать отслеживаемый товар, редактируется список URL прямо
  в этом файле — других источников списка нет.
