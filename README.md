# «Умный друг» — AI-репетитор по математике

Рабочий прототип для одного ученика 3 класса. Desktop-приложение ведёт короткий диалог, а backend управляет ходом занятия, сохраняет историю в SQLite, ищет материалы в локальном индексе учебника и обращается к любому OpenAI-compatible LLM API.

## Варианты интерфейса

- `main` — презентационная демо-версия с заполненными карточками для быстрой оценки дизайна.
- `real-statistics` — версия без демонстрационных значений; главная, задачи, прогресс и родительский экран заполняются только данными сохранённых занятий.

## Архитектура

```text
PySide6 desktop ── HTTP/REST ── FastAPI ── OpenAI-compatible API
                                   │
                             SQLite + JSON-индекс PDF
```

API-ключ хранится только в `.env` backend. Desktop знает лишь `BACKEND_URL`.

## Быстрый запуск на Windows

Нужен Python 3.12. Из корня проекта:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements-dev.txt
pip install -r desktop\requirements.txt
Copy-Item backend\.env.example backend\.env
Copy-Item desktop\.env.example desktop\.env
```

Заполните `backend/.env`:

```dotenv
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=ваш_ключ
LLM_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./data/tutor.db
TEXTBOOK_INDEX=../data/textbooks/index.json
```

`LLM_BASE_URL` должен указывать на корень API, содержащий endpoint `/chat/completions`. Для локального или другого совместимого сервиса поменяйте URL и имя модели. Ключ не должен попадать в desktop-конфигурацию.

Запустите backend в первом терминале:

```powershell
cd backend
uvicorn app.main:app --reload
```

Во втором терминале:

```powershell
cd desktop
python -m app.main
```

Если backend находится на другом компьютере, укажите в `desktop/.env`, например, `BACKEND_URL=https://tutor.example.ru`.

## Учебник

Положите PDF в `data/textbooks/`, затем из корня выполните:

```powershell
python scripts/index_textbook.py data/textbooks/math-3.pdf
```

Скрипт извлекает текст, режет его с небольшим перекрытием и создаёт `data/textbooks/index.json`. Сканированный PDF без текстового слоя сначала потребует OCR. Поиск вынесен в `backend/app/textbook.py`, чтобы позднее заменить его embeddings/vector DB.

## Docker (только backend)

Создайте `backend/.env`, затем:

```powershell
docker compose up --build
```

SQLite хранится в `backend/data`, индекс монтируется из `data/textbooks`.

## API

```powershell
$lesson = Invoke-RestMethod -Method Post http://localhost:8000/api/session/new

Invoke-RestMethod -Method Post http://localhost:8000/api/chat `
  -ContentType 'application/json' `
  -Body (@{session_id=$lesson.session_id; message='Как решить 36 + 27?'} | ConvertTo-Json)

Invoke-RestMethod http://localhost:8000/api/session/$($lesson.session_id)/messages
Invoke-RestMethod -Method Post http://localhost:8000/api/session/$($lesson.session_id)/finish
```

Swagger UI доступен на `http://localhost:8000/docs`, проверка сервиса — `GET /health`.

## Состояния репетитора

Правила находятся в `backend/app/tutor.py`. Простая машина состояний последовательно использует оценку понимания, наводящие вопросы, обычную и сильную подсказки и лишь после нескольких попыток разрешает пошаговое решение. LLM получает текущее состояние как строгое ограничение; переходами управляет код, а не сама модель.

## Тесты

```powershell
cd backend
pytest -q
```

В тестах используется поддельный LLM, внешние API не вызываются.

Smoke-тест desktop UI (навигация, занятие и размеры окна):

```powershell
python -m pytest -q desktop\tests
```

Детерминированные скриншоты всех страниц можно обновить командой `python scripts\capture_desktop_ui.py`.

## Сборка desktop в `.exe`

```powershell
pip install pyinstaller
cd desktop
pyinstaller --noconfirm --clean AI-Tutor.spec
```

Результат появится как `desktop/dist/AI-Tutor.exe`. Spec включает маскота, SVG-иконки и Windows icon. Файл можно перенести отдельно; для изменения адреса backend положите рядом с ним `.env` с `BACKEND_URL`.

## Основные файлы

- `backend/app/main.py` — REST API и жизненный цикл данных.
- `backend/app/tutor.py` — педагогические правила, состояния и LLM-контекст.
- `backend/app/textbook.py` — локальный поиск по учебнику.
- `backend/app/llm.py` — OpenAI-compatible клиент.
- `desktop/app/ui/` — страницы, sidebar, виджеты и тема PySide6.
- `desktop/app/services/` — фоновые HTTP-запросы и временные dashboard-данные.
- `scripts/index_textbook.py` — индексатор PDF.

## Ограничения MVP и следующий этап

Это прототип для одного ребёнка, одного предмета и одного процесса backend. Авторизации, OCR, потоковой выдачи, продвинутой модерации и семантического поиска пока нет. Итог занятия формируется детерминированно из истории, поэтому не зависит от дополнительного LLM-вызова.

Следующим этапом логично добавить структурированную оценку ответа моделью (с валидацией JSON), профиль навыков ребёнка, OCR для сканов и embeddings-поиск; затем — аутентификацию backend, HTTPS и родительский экран.
