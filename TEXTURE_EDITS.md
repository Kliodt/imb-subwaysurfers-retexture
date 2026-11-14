# Текущая сине-бело-графитовая переработка

**Редакция5:** восстановлен рисунок звезды x2. Монета MEGA BATTLE перенесена в отдельный свободный участок props_tex78; обновлять PNG78 и coin-branding.json вместе, затем пересобирать игру/образ. [Проверки](agent-reports/X2_STAR_RESTORE_STATUS.md).

**UI-монеты:**116 HighResAtlas и154 LowResAtlas теперь содержат MEGA BATTLE в21 денежном спрайте каждый. Альфа/разметка и прочие334 спрайта каждого атласа сохранены; сборка обновлена. [Отчёт](agent-reports/UI_COIN_BRANDING_STATUS.md).

**Редакция4:** монета MEGA BATTLE, без ITMO. Исправлены направления U на обеих сторонах относительно зеркальной версии3. Обновлять PNG78, texture_tool.py и coin-branding.json вместе; пересобрать образ и перезапустить контейнер.

**14 ноября, редакция3:** монета ITMO MEGA BATTLE без [now]; граффити48 с новым естественным прозрачным контуром. PNG78,48 и textures/coin-branding.json/edit-policy.json коммитить вместе с texture_tool.py: build теперь также корректирует зеркальные лицевые UV монеты. [Подробности](agent-reports/GRAFFITI_ITMO_STATUS.md).

**14 ноября2026, редакция2:** граффити48 переделано в агрессивное уличное ITMO / MEGA / BATTLE — рубленые буквы, обводки, потёки/брызги, объёмные синие тени. Сборка обновлена. [Отчёт](agent-reports/GRAFFITI_ITMO_STATUS.md).

**Независимая проверка:** 90 файлов без статических замечаний, 9 рисков, 3 дефекта. PNG не менялись; перечень и дальнейшие действия — [QA_REPORT.md](agent-reports/QA_REPORT.md), актуальные статусы — ONBOARDING.md.

13 ноября 2026: рассмотрены все 102 PNG. Установлены 70 новых текстур по шести референсам exampleImages; 32 технических ресурса/флаги оставлены исходными с причинами в [ONBOARDING.md](ONBOARDING.md). Работу выполнили шесть субагентов, подробности в agent-reports/WORLD_STATUS.md, agent-reports/BOARDS_STATUS.md, agent-reports/CHARACTERS_STATUS.md, agent-reports/EFFECTS_STATUS.md, agent-reports/UI_ELEMENTS_STATUS.md и UI_ATLASES_STATUS.md.

68 PNG переработаны imagegen. Для HighResAtlas/LowResAtlas пользователь явно выбрал программную перекраску: scripts/recolor_ui_atlases.py выполняет только попиксельное преобразование цвета, сохраняя геометрию и нейтральные символы. Генеративные версии этих атласов отклонены из-за сдвига спрайтов.

Исправлены несовпадение логотипа48 с альфой, смещение цветов58, разрыв талии Jake110; тёплая трапеция и красные метки60 также приведены к новой палитре. Размеры и исходная альфа всех102 PNG проверены относительно a9cdde1.

Финальная build: 70 изменённых ресурсов, 44406 объектов, точное RGBA-совпадение после повторного чтения пакета. Проверка в игровом меню и забеге ещё требуется: статический QA не доказывает корректность всех UV, тайлинга и материалов.

## История: пробная красная окраска

**Историческое состояние перед новой переработкой:** по просьбе пользователя исходные текстуры восстановлены из `a9cdde1`, обе локальные копии игры обновлены. Ниже сохранена история эксперимента, а не текущее состояние. Дальнейшая инструкция: [TEXTURE_GUIDE.md](TEXTURE_GUIDE.md).

Состояние эксперимента в `5cba8da`: четыре атласа (поезда, стартовый поезд, упрощённые поезда и окружение) полностью заполнены точным цветом RGBA (255, 0, 0, 255), без рисунка. По прямому указанию «буквально залей холст» использована одноцветная заливка. Все четыре текстуры прочитаны обратно и проверены.

Исходное состояние: коммит `a9cdde1`.

Изменены только PNG поездов и окружения Zurich. Готовая версия: `game-local/`.
Для просмотра: http://127.0.0.1:8766/game-local/ (обновить Ctrl+F5).

Изображения отредактированы встроенным генератором изображений и приведены к исходным размерам 512×512 и 1024×1024.

Промпт окружения: Edit target: provided 1024x1024 game UV texture atlas. Apply only a modest but clearly visible red tint across existing textures. Preserve EXACT atlas positions, boundaries, all details, layout, shapes, and dimensions 1024x1024. This is a drop-in texture used by existing 3D UV maps, never rearrange or redraw any shapes. Keep dark unused background unchanged. No new objects. Color correction only.

Промпт поездов: Edit only colors in this game UV texture atlas. Add a visible gentle red tint to train surfaces and swatches, including formerly blue windows. Keep exact texture island positions and sizes, grey empty background, shading, boundaries and details. Do not add or remove anything, do not change layout. Output square drop-in texture, same composition. Color correction only.

Проверка сборки: обе изменённые текстуры прочитаны обратно из пакета, RGB совпадает с PNG, число объектов осталось 44406. Игровой забег с этой окраской не проверялся.

Для возврата позже: отменить коммит с окраской и выполнить `python texture_tool.py build`.
