# Отчёты агентов

Здесь собраны все рабочие отчёты и проверки. Новые отчёты сохранять в эту папку, не в корень проекта. Главный реестр статусов остаётся в [ONBOARDING.md](../ONBOARDING.md).

## С чего начать

- [X2_STAR_RESTORE_STATUS.md](X2_STAR_RESTORE_STATUS.md) — восстановлена звезда x2; брендинг монеты отделён от общего участка атласа.

- [UI_COIN_BRANDING_STATUS.md](UI_COIN_BRANDING_STATUS.md) — MEGA BATTLE в21 спрайте каждого из HighResAtlas/LowResAtlas.

- [GRAFFITI_ITMO_STATUS.md](GRAFFITI_ITMO_STATUS.md) —14.11: новое граффити ITMO / MEGA / BATTLE; прежний независимый QA48 не актуален.

- [QA_REPORT.md](QA_REPORT.md) — сводка независимого аудита: 90 без статических замечаний, 9 рисков, 3 дефекта.
- [QA_TECHNICAL.md](QA_TECHNICAL.md) — проверка размеров, прозрачности и объектов Unity.
- [QA_SUMMARY.json](QA_SUMMARY.json) — машинная сводка всех 102 PNG.

## Отчёты по группам

| Группа | Работа с текстурами | Независимая проверка |
| --- | --- | --- |
| Мир и поезда | [WORLD_STATUS.md](WORLD_STATUS.md) | [QA_WORLD.md](QA_WORLD.md) |
| Доски и bobble | [BOARDS_STATUS.md](BOARDS_STATUS.md) | [QA_BOARDS.md](QA_BOARDS.md) |
| Персонажи | [CHARACTERS_STATUS.md](CHARACTERS_STATUS.md) | [QA_CHARACTERS.md](QA_CHARACTERS.md) |
| Эффекты | [EFFECTS_STATUS.md](EFFECTS_STATUS.md) | [QA_UI_EFFECTS.md](QA_UI_EFFECTS.md) |
| Элементы интерфейса | [UI_ELEMENTS_STATUS.md](UI_ELEMENTS_STATUS.md) | [QA_UI_EFFECTS.md](QA_UI_EFFECTS.md) |
| UI-атласы | [UI_ATLASES_STATUS.md](UI_ATLASES_STATUS.md) | [QA_UI_EFFECTS.md](QA_UI_EFFECTS.md) |

У независимых групп есть одноимённые JSON с результатами по файлам; QA_TECHNICAL.json хранит технические данные и SHA256. В текстах и JSON пути textures/, output/, scripts/ считаются относительно корня проекта. Промежуточные картинки и сравнения уже сгруппированы в output/ и сюда не дублируются.

Повторная техническая проверка из корня: `python scripts/audit_texture_package.py`. Она сохраняет JSON в эту папку. Сводки и статусы описывают конкретное проверенное состояние; после изменения PNG нужно провести новую проверку и обновить основной реестр.
