# Инструкция агенту: изменение текстур Subway Surfers Zurich

## Текущее состояние и проверенные факты

Игра возвращена к исходным текстурам. Обе папки `game-local/` и `game-demo/` сейчас содержат сборку без пробной окраски. Пользователь подтвердил, что сплошная красная заливка атласов действительно отображалась в игре.

Это готовая Unity WebGL-сборка, а не исходный Unity-проект. Для замены текстур Unity Editor и перекомпиляция игрового кода не нужны: меняются ресурсы, WebAssembly-код остаётся исходным. Поддержка этого инструмента настроена только на Zurich; наличие других городов в репозитории не означает, что команда build меняет их тоже.

Рабочий корень: `C:\Users\79215\Desktop\Gaba_Projects\megaorg\subwaysurfers`.

## Куда смотреть

| Путь от корня | Назначение |
| --- | --- |
| `subway-original/` | Исходный репозиторий https://github.com/bubbls/subwaysurfersmerge, отдельный вложенный Git. Не редактировать для обычной замены текстур. |
| `textures/` | 102 редактируемых PNG из пакета Zurich. Именно эти файлы читает build. |
| `textures/catalog.json` | Полный машинный каталог: имя PNG, имя Texture2D в Unity, ширина и высота. |
| `texture_tool.py` | Извлечение и перепаковка ресурсов через UnityPy. |
| `launcher-template.html` | Шаблон локальной страницы без удалённого base URL. |
| `game-local/` | Результат команды build, открывать эту версию для своих правок. |
| `game-demo/` | Дополнительная сборка. Сейчас также восстановлена; команда demo снова создаст старую фиолетовую перекраску поездов, независимо от PNG. |
| `.tools/python/` | Локальные зависимости Python, включая UnityPy 1.25.4 и Pillow. |

Основной ресурс: `ZurichNewPrivacy.data.unityweb`. Функция `source()` сначала берёт цельный файл из `subway-original/zurich/`; если его нет, соединяет `.part1` и `.part2` из корня `subway-original/` в указанном порядке. Поэтому правка только split-файлов не подействует, если цельный файл существует.

Пакет имеет заголовок `UnityWebData1.0`. В нём находятся `data.unity3d`, `Resources/unity_default_resources`, `resources.resource`, `sharedassets1.resource`, метаданные и другие служебные данные. UnityPy раскрывает вложенные сериализованные файлы `sharedassets0.assets`, `sharedassets1.assets` и `resources.assets`. Файлы `.resource` могут содержать вынесенные байты изображений; не редактировать их вручную.

Имя PNG имеет структуру `<serialized_file>_<path_id>_<texture_name>.png`. Например, `sharedassets1.assets_46_1.101.0_Zurich_trains.png` — объект Texture2D с path_id 46 из `sharedassets1.assets`. Префикс 1.101 в именах текстур не надо исправлять: это фактические имена ресурсов, хотя JSON сборки сообщает productVersion 1.94.0.

## Как менять и запускать

Все команды выполнять из корня проекта в PowerShell.

1. Проверить `git status --short`, сохранить пользовательские правки или сделать коммит перед экспериментом.
2. Выбрать PNG по таблицам ниже и визуально осмотреть. Не переименовывать файлы, не менять размер холста, ориентацию и альфа-канал. Атлас содержит участки для множества объектов: нельзя перемещать рисунки между участками, иначе UV-развёртка начнёт брать неправильные пиксели.
3. Редактировать PNG в `textures/`.
4. Собрать:

```powershell
python texture_tool.py build
```

Команда каждый раз загружает чистый исходный пакет и применяет только PNG, отличающиеся от оригинала. Удалённый PNG не удаляет ресурс, а оставляет исходную текстуру. Вывод `changed: []` означает отсутствие изменений; при правках должны появиться нужные имена текстур.

Изменённые изображения записываются в RGBA32 (`target_format=4`), с пересозданием mip-уровней по исходному количеству. Это сохраняет прозрачность и избегает потерь сжатия, но может увеличить размер сборки и потребление памяти. Неизменённые текстуры остаются в исходном формате.

Затем build записывает `game-local/ZurichNewPrivacy.data.unityweb`, копирует исходный WASM, framework, загрузчики и SDK, создаёт локальный index.html. Пакет повторно читается: проверяется количество объектов и RGB изменённых текстур. Текущая проверка не сравнивает альфа-канал и не заменяет визуальную проверку в игре.

5. Если локальный сервер ещё не запущен:

```powershell
python -m http.server 8766 --bind 127.0.0.1
```

Оставить процесс работающим. Открыть http://127.0.0.1:8766/game-local/ и обновить Ctrl+F5. Не открывать HTML через file:// и не проверять старую CDN-страницу — она не использует местный пакет. При старой картинке проверить URL, выполнить жёсткое обновление; при необходимости использовать новое приватное окно, чтобы исключить кэш/сохранения Unity. Если порт занят уже работающим сервером этого проекта, повторно запускать его не нужно.

6. Убедиться в игре, что изменились нужные объекты, включая стартовый поезд и дальние поезда. Механика и геометрия от изменения текстур не меняются. Цвет материалов, освещение и шейдер могут менять видимый оттенок относительно PNG.
7. Сделать отдельный коммит с текстурами и описанием. `game-local/`, `game-demo/`, `.tools/` и исходный вложенный репозиторий исключены из корневого Git; сборку нужно пересоздавать после отката PNG.

Если зависимостей нет:

```powershell
python -m pip install --target .tools/python UnityPy==1.25.4
```

## Как вернуть исходное состояние

Исходные PNG сохранены в корневом коммите `a9cdde1`. При необходимости, предварительно сохранив нужные новые правки:

```powershell
git restore --source=a9cdde1 -- textures
python texture_tool.py build
```

Это восстанавливает только каталог текстур, не переписывает историю Git. Проверить `changed: []`, затем Ctrl+F5 в браузере.

Альтернативная команда `python texture_tool.py export` заново извлекает исходные 102 PNG, но **перезаписывает все текущие изображения в textures/**. Не выполнять export после редактирования без сохранения нужных правок. Команда `demo` не собирает пользовательские PNG и для обычной работы не нужна.

## Какие текстуры где находятся

Пути в таблицах ниже указаны относительно `textures/`. Имена, размеры и принадлежность Unity-файлам получены из реального пакета. Назначение некоторых изображений следует только из имени: точная привязка к материалам и UV-участкам не исследована.

Подтверждены практическим тестом четыре атласа:

| PNG | Размер | Назначение |
| --- | --- | --- |
| `sharedassets1.assets_46_1.101.0_Zurich_trains.png` | 512×512 | Основные текстуры поездов; цветовые полосы, окна и другие участки. |
| `sharedassets1.assets_48_1.101.0_Zurich_train_start.png` | 1024×1024 | Атлас стартового поезда, важен для видимых изменений в начале игры. |
| `sharedassets1.assets_60_1.101.0_Zurich_trains_low.png` | 512×512 | Упрощённый вариант поездов, по имени — для low-detail отображения. Конкретные расстояния переключения не проверялись. |
| `sharedassets1.assets_58_1.101.0_Zurich_environment.png` | 1024×1024 | Окружение: стены/мощение, двери, деревянные поверхности, ставни, цветы, цветовые полосы. Точный список моделей не составлен. |

Остальные полезные группы:

| Unity-файл / имена текстур | Где искать и что предположительно меняют |
| --- | --- |
| `sharedassets1.assets`: `waterReflection`, `waterfall` | Вода, отражения, водопад Zurich. |
| `sharedassets1.assets`: `Zurich_enemies` | Атлас enemies; нельзя автоматически считать это текстурой Джейка. Нужна проверка материалов/моделей. |
| `sharedassets1.assets`: `Default-Particle`, `teleboardFX`, `jetpackSmoke`, `paintSpray`, `grindsparkFX`, `lavaGlowingParticle` | Эффекты частиц, дым, краска, искры, свечение. |
| `sharedassets1.assets`: `railRamp`, `flyingBird_tex` | Рампа/рельсовый элемент и птица по именам. |
| `sharedassets0.assets`: `GenericAtlas` | Общий атлас; состав надо смотреть в PNG. |
| `sharedassets0.assets`: `1.91_NewYork_load_splash_v2` | Заставка загрузки; имя NewYork реально присутствует в пакете Zurich. |
| `resources.assets`: `HighResAtlas`, `LowResAtlas`, `HighResCountriesAtlas` | Большие общие/интерфейсные атласы; для отдельных кнопок нужны координаты участков. |
| `resources.assets`: `props_tex`, `amsterdam_prop_tex` | Общие предметы и дополнительные поверхности по именам; точная привязка не проверена. |
| `resources.assets`: `board_*_tex` | Текстуры различных ховербордов. Маленькие изображения часто являются палитрами, а не обычными рисунками доски. |
| `resources.assets`: `icon_00_Brody`, `icon_03_Ninja`, `icon_11_Tricky` и другие `icon_*` | Иконки персонажей в интерфейсе, не обязательно текстуры их 3D-моделей. |
| `resources.assets`: `img_char_jake`, `char_king`, `ageRestriction_characterHeader`, `img_track` | Отдельные изображения персонажей/заголовка/трассы в интерфейсе по именам. Замена img_char_jake не доказывает замену одежды бегущего 3D-персонажа. |
| `resources.assets`: `front_icon_*`, `scoreboard`, `event_bg`, `awards_bg`, `mysterybox_bg`, `*_mask` | Интерфейс, фоны, иконки и маски. Сохранять прозрачность. |
| `resources.assets`: `effects_tex`, `trail*`, `shineAdditive`, `spraySplash`, `material_effect_puff` | Следы, блики, брызги и прочие эффекты. |

Для точной замены одежды 3D-персонажа сначала исследовать `Material` → ссылки на `Texture2D`, затем материалы соответствующего renderer/mesh. Эти связи инструмент пока не экспортирует. Не выдавать предположение по имени файла за подтверждённую связь.

## Полный каталог PNG

Следующая таблица содержит все 102 файла, сгруппированные по исходному сериализованному Unity-файлу. Для поиска по имени также использовать `textures/catalog.json`.

### sharedassets0.assets

| PNG в textures/ | Размер |
| --- | --- |
| `sharedassets0.assets_7_GenericAtlas.png` | 512×512 |
| `sharedassets0.assets_9_1.91_NewYork_load_splash_v2.png` | 1024×1024 |

### sharedassets1.assets

| PNG в textures/ | Размер |
| --- | --- |
| `sharedassets1.assets_44_Default-Particle.png` | 64×64 |
| `sharedassets1.assets_45_teleboardFX.png` | 16×16 |
| `sharedassets1.assets_46_1.101.0_Zurich_trains.png` | 512×512 |
| `sharedassets1.assets_47_1.101.0_Zurich_waterReflection.png` | 512×256 |
| `sharedassets1.assets_48_1.101.0_Zurich_train_start.png` | 1024×1024 |
| `sharedassets1.assets_49_material_effect_paintSpray.png` | 128×128 |
| `sharedassets1.assets_50_celebration_background.png` | 64×1 |
| `sharedassets1.assets_51_jetpackSmoke.png` | 128×32 |
| `sharedassets1.assets_52_1.101.0_Zurich_waterfall.png` | 64×128 |
| `sharedassets1.assets_54_railRamp.png` | 16×32 |
| `sharedassets1.assets_55_lavaGlowingParticle.png` | 64×64 |
| `sharedassets1.assets_56_white.png` | 32×32 |
| `sharedassets1.assets_57_grindsparkFX.png` | 256×256 |
| `sharedassets1.assets_58_1.101.0_Zurich_environment.png` | 1024×1024 |
| `sharedassets1.assets_59_0.00_Generic_flyingBird_tex.png` | 16×32 |
| `sharedassets1.assets_60_1.101.0_Zurich_trains_low.png` | 512×512 |
| `sharedassets1.assets_61_celebration_stripe.png` | 256×16 |
| `sharedassets1.assets_62_1.101.0_Zurich_enemies.png` | 512×512 |

### resources.assets

| PNG в textures/ | Размер |
| --- | --- |
| `resources.assets_74_effects_tex.png` | 128×64 |
| `resources.assets_75_emblem_halloween.png` | 196×220 |
| `resources.assets_76_trailAlpha.png` | 256×256 |
| `resources.assets_77_event_bg.png` | 128×128 |
| `resources.assets_78_props_tex.png` | 512×512 |
| `resources.assets_79_board_RioHD_tex.png` | 16×32 |
| `resources.assets_80_board_windglider_tex.png` | 32×32 |
| `resources.assets_81_circle_bg_mask.png` | 100×100 |
| `resources.assets_82_icon_key_cloud_mask.png` | 88×64 |
| `resources.assets_83_bobbleMiami.png` | 32×32 |
| `resources.assets_84_shineAdditive.png` | 64×64 |
| `resources.assets_85_selector.png` | 64×64 |
| `resources.assets_86_icon_00_Brody.png` | 256×256 |
| `resources.assets_87_icon_03_Ninja.png` | 256×256 |
| `resources.assets_88_board_scoot_tex.png` | 32×32 |
| `resources.assets_89_scoreboard.png` | 512×256 |
| `resources.assets_90_background_glow_smb_straight.png` | 32×32 |
| `resources.assets_91_icon_05_KIng.png` | 256×256 |
| `resources.assets_92_board_starterpack_tex.png` | 64×64 |
| `resources.assets_93_trail.png` | 256×256 |
| `resources.assets_94_material_effect_puff.png` | 128×128 |
| `resources.assets_95_whitebox.png` | 3×3 |
| `resources.assets_96_board_superhero_tex.png` | 32×32 |
| `resources.assets_97_icon_07_Yutani.png` | 256×256 |
| `resources.assets_98_board_hotRod_tex.png` | 32×32 |
| `resources.assets_99_front_icon_shop.png` | 256×256 |
| `resources.assets_100_ssBlurred.png` | 512×512 |
| `resources.assets_101_board_star_tex.png` | 64×64 |
| `resources.assets_102_board_londonExtra_tex.png` | 32×32 |
| `resources.assets_103_icon_star.png` | 20×19 |
| `resources.assets_104_icon_08_Spike.png` | 256×256 |
| `resources.assets_105_board_daredevil_tex.png` | 32×32 |
| `resources.assets_106_video_button_tv_icon_mask.png` | 85×104 |
| `resources.assets_108_board_skullfire_tex.png` | 32×32 |
| `resources.assets_109_bobble.png` | 32×32 |
| `resources.assets_110_img_char_jake.png` | 280×404 |
| `resources.assets_111_icon_friend.png` | 64×64 |
| `resources.assets_112_mysterybox_bg.png` | 1024×1024 |
| `resources.assets_113_background_frame_blur.png` | 35×13 |
| `resources.assets_114_background_sticker_medium_mask.png` | 114×114 |
| `resources.assets_115_icon_04_Lucy.png` | 256×256 |
| `resources.assets_116_HighResAtlas.png` | 2048×1024 |
| `resources.assets_117_board_bouncer_tex.png` | 32×32 |
| `resources.assets_118_hunt_prize_bg.png` | 128×4 |
| `resources.assets_119_awards_bg.png` | 512×512 |
| `resources.assets_120_board_greatWhite_tex.png` | 32×32 |
| `resources.assets_121_icon_01_Tagbot.png` | 256×256 |
| `resources.assets_122_icon_mystery_box_mask.png` | 146×136 |
| `resources.assets_123_double_coins_button_mask.png` | 246×59 |
| `resources.assets_124_trail2.png` | 256×256 |
| `resources.assets_125_board_teleporter_tex.png` | 32×32 |
| `resources.assets_126_Fade.png` | 32×3 |
| `resources.assets_127_amsterdam_prop_tex.png` | 4×16 |
| `resources.assets_128_board_sunset_tex.png` | 32×32 |
| `resources.assets_129_front_icon_top_run.png` | 512×256 |
| `resources.assets_130_icon_02_Tasha.png` | 256×256 |
| `resources.assets_131_butterfly_idleScreen_tex.png` | 32×64 |
| `resources.assets_132_ageRestriction_characterHeader.png` | 512×256 |
| `resources.assets_133_background_glow_award.png` | 256×256 |
| `resources.assets_134_icon_star.png` | 40×38 |
| `resources.assets_135_spraySplash.png` | 64×64 |
| `resources.assets_136_board_lowrider_tex.png` | 64×64 |
| `resources.assets_137_board_lumberjack_tex.png` | 32×32 |
| `resources.assets_139_icon_small_mini_mysteryBox_mask.png` | 54×52 |
| `resources.assets_140_front_icon_MyTour.png` | 256×128 |
| `resources.assets_141_board_snowboard_tex.png` | 64×64 |
| `resources.assets_142_GenericMenuColors.png` | 4×4 |
| `resources.assets_143_icon_09_Fresh.png` | 256×256 |
| `resources.assets_144_tokyo_stripe.png` | 10×448 |
| `resources.assets_145_Icon_coin_pouch_large_mask.png` | 52×70 |
| `resources.assets_146_front_icon_me.png` | 256×256 |
| `resources.assets_147_welcome_pack_main_button_mask.png` | 64×64 |
| `resources.assets_148_board_bigKahuna_tex.png` | 32×64 |
| `resources.assets_149_board_default_tex.png` | 32×32 |
| `resources.assets_150_board_tokyoExtra_tex.png` | 64×64 |
| `resources.assets_151_icon_11_Tricky.png` | 256×256 |
| `resources.assets_152_HighResCountriesAtlas.png` | 1024×1024 |
| `resources.assets_153_char_king.png` | 276×268 |
| `resources.assets_154_LowResAtlas.png` | 1024×512 |
| `resources.assets_155_img_track.png` | 480×156 |
| `resources.assets_156_board_monster_tex.png` | 32×32 |
| `resources.assets_157_MissionsFont_small-export.png` | 256×256 |
