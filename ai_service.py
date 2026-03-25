import os
import json
import random
import re
from typing import Dict, Any, List

# Public data: list of objection types and their scenarios
OBJECTION_TYPES = ["price", "competitor", "technical", "trust", "complexity", "churn"]

# Scenarios: 5 per type, each with soft and firm replies.
# These are handcrafted to feel natural and avoid canned templates.
SCENARIOS: Dict[str, List[Dict[str, str]]] = {
    "price": [
        {"soft": "Понимаю, бюджет важен. Давайте посчитаем TCO по вашим оборотам — вдруг на практике выйдет выгоднее.",
         "firm": "Цена имеет значение, но давайте посчитаем окупаемость и экономию по вашим оборотам — цифры скажут правду."},
        {"soft": "Сейчас многие сравнивают стоимость. Мы можем рассчитать и показать, где экономия за год.",
         "firm": "Мы укажем конкретную экономию по вашим оборотам и срок окупаемости — без двойных условий."},
        {"soft": "Я понимаю вопрос про цену. Часто выгода кроется в снижении потерь и ускорении операций.",
         "firm": "Цена — это правда, но наш фокус — на ROI: сколько вы экономите за счет скорости и меньших ошибок."},
        {"soft": "Готов разобрать с вами детали и сравнить прозрачные цифры, не путая условия.",
         "firm": "Если у конкурентов ниже цена, скажите — мы приведем сравнение по функционалу и экономике."},
        {"soft": "Давайте посчитаем на ваших данных и увидим реальную экономию.",
         "firm": "Цена важна, но окупаемость и поддержка дают долгосрочную ценность — посмотрим цифры."},
    ],
    "competitor": [
        {"soft": "Понимаю, у конкурентов может быть что-то похожее. Давайте сравним по фактам." ,
         "firm": "Признано: конкуренты есть. Но мы сравним по ключевым метрикам: скорость расчетов, сервис, поддержка."},
        {"soft": "Хочется увидеть преимущества именно нашего решения.",
         "firm": "Мы покажем, чем наше предложение выгоднее для вашей ниши и оборотов."},
        {"soft": "С чем сравниваете именно: скорость, комиссии, или интеграции?",
         "firm": "Сделаем детальное сравнение по параметрам, которые важны вам."},
        {"soft": "Готов привести независимую аналитику по аналогичным кейсам.",
         "firm": "Наше преимущество — устойчивость и поддержка на старте. Давайте разберемся."},
        {"soft": "А как вы оцениваете качество поддержки у конкурентов?",
         "firm": "Мы покажем, как у нас работает техподдержка и SLA — цифры на глазах."},
    ],
    "technical": [
        {"soft": "Сбой — неприятно. Что именно не работает у вас сейчас?",
         "firm": "Разберем проблему по шагам и найдем надежное решение без просто обещаний."},
        {"soft": "Технические вопросы часто возникают на старте. Договоримся устранить их быстро.",
         "firm": "Мы устраним проблемы в процессе внедрения и дадим четкие регламентированные шаги."},
        {"soft": "Опишите, что именно не так; мы быстро найдём обходные решения.",
         "firm": "Сформируем план исправления и снизим риск повторения проблемы."},
        {"soft": "Где именно произошёл сбой: терминал, интеграция, или параметры аккаунта?",
         "firm": "Уточним причину и предложим конкретные действия для быстрого восстановления."},
        {"soft": "Проблемы с интеграцией — классика. Мы помогаем до запуска.",
         "firm": "Наши инженеры помогут быстро пройти интеграцию без потерь времени."},
    ],
    "trust": [
        {"soft": "Понимаю, доверие к новому партнеру не приходит сразу.",
         "firm": "Мы покажем кейсы и гарантии, чтобы вы увидели реальную надежность."},
        {"soft": "Что в нашем сервисе вызывает сомнение?",
         "firm": "Мы дадим прозрачные условия, SLA и доступ к истории операций."},
        {"soft": "Кратко: почему стоит поверить в нас?",
         "firm": "Мы предлагаем полный контроль и проверяемые результаты за первый месяц."},
        {"soft": "Надежность важна. Готовы показать доказательства?",
         "firm": "Дикие обещания уступают делу: у нас проверяемые показатели и поддержка 24/7."},
        {"soft": "Как у вас обычно выстраивают доверие?",
         "firm": "Мы предлагаем прозрачность по каждому KPI и отзывам клиентов."},
    ],
    "complexity": [
        {"soft": "Да, адаптация может казаться сложной. Разберёмся по шагам.",
         "firm": "Упростим задачу: разбиваем внедрение на 4 модуля и дадим готовые сценарии."},
        {"soft": "Сложности понятны. Какие процессы вы хотите автоматизировать в первую очередь?",
         "firm": "Сфокусируемся на критичных операциях и минимизируем паузу внедрения."},
        {"soft": "Видим риски. Какие из функций для вас критичны?",
         "firm": "Расставим приоритеты и внедрим по этапам с проверками."},
        {"soft": "Есть варианты уменьшить сложность на старте.",
         "firm": "Предложим готовые модули и миграцию без перерыва в работу."},
        {"soft": "Масштабирование часто вызывает вопросы.",
         "firm": "Мы предлагаем модульную архитектуру и понятную документацию."},
    ],
    "churn": [
        {"soft": "Понимаю, вы хотите уйти. Что стало последней точкой напряжения?",
         "firm": "Давайте обсудим, как удержать вас: что можно улучшить за 30 дней."},
        {"soft": "Жаль терять клиента. Что именно повлияло на решение?",
         "firm": "Мы исправим проблему и предложим компенсацию за потери."},
        {"soft": "Если сейчас уйдёте, вы упустите ценность нашего сервиса.",
         "firm": "Дадим перерасчет условий под ваш объём и требования."},
        {"soft": "Хорошо, давайте попробуем другое решения.",
         "firm": "Мы предложим адаптацию и персональные условия, попробуйте 30-дневный пилот."},
        {"soft": "Условия не совпали с ожиданиями?",
         "firm": "Посмотрим детали и подстроим условия под ваш бизнес."},
    ],
}

# Very lightweight NLP-like helpers (offline)
KEYWORDS = {
    'price': ['дорого', 'цена', 'стоимость', 'комиссия', 'price', 'cost'],
    'competitor': ['конкурент', 'конкурентов', 'уровень', 'кто', 'comparison'],
    'technical': ['сбой', 'терминал', 'интеграция', 'интегрироваться', 'ошибка'],
    'trust': ['не доверяю', 'недоверие', 'неверю', 'страх'],
    'complexity': ['сложно', 'сложный', 'трудно', 'гаджет'],
    'churn': ['уйти', 'хочу уйти', 'уход', 'не устраивает']
}

def analyze_message(text: str) -> Dict[str, Any]:
    t = text.lower()
    keywords = []
    for k, words in KEYWORDS.items():
        for w in words:
            if w in t:
                keywords.append(k)
                break
    # tone heuristic
    tone = 'neutral'
    if any(w in t for w in ['не','нет','не могу','не хочу','жалу']) or any(w in t for w in ['скепт', 'сомневаюсь','не верю','не доверяю','не доверится']):
        tone = 'negative'
    elif '?' in text:
        tone = 'curious'
    # intent heuristic
    intent = 'интерес'
    if any(w in t for w in ['что', 'как', 'почему', 'зачем', '?']):
        intent = 'вопрос'
    if any(w in t for w in ['уйти', 'исключить', 'перестать']):
        intent = 'уход'
    if any(w in t for w in ['сравн', 'сравнение', 'почему выбрать', 'чем']):
        intent = 'сравнение'
    return {'keywords': keywords, 'tone': tone, 'intent': intent}


def classify_objection(text: str) -> str:
    t = text.lower()
    # simple heuristic: choose the first matching type
    for ob_type, words in KEYWORDS.items():
        for w in words:
            if w in t:
                return ob_type
    # fallback based on detected intent
    if 'дорого' in t or 'цена' in t:
        return 'price'
    if 'конкур' in t:
        return 'competitor'
    if 'сбой' in t or 'терминал' in t:
        return 'technical'
    if 'недовер' in t or 'страх' in t:
        return 'trust'
    if 'сложно' in t or 'сложн' in t:
        return 'complexity'
    if 'уйти' in t or 'уход' in t:
        return 'churn'
    return 'price'


def detect_stage(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ['сравн', 'сравнение', 'почему выбрать', 'чем']) or 'как' in t:
        return 'сравнение'
    if any(w in t for w in ['дорого','цена','стоимость','комиссия','price']) or 'почему' in t:
        # could be price-related, but a mild stage as возражение
        return 'возражение'
    if any(w in t for w in ['не доверяю','недоверие','страх']) or 'trust' in t:
        return 'критическое возражение'
    if any(w in t for w in ['уйти','хочу уйти','уход']):
        return 'уход'
    return 'интерес'


def generate_reply(client_message: str, history: List[Dict[str, str]], mode: str = 'OFFLINE') -> Dict[str, Any]:
    # Normalize inputs
    stage = detect_stage(client_message)
    objection_type = classify_objection(client_message)
    # Choose a scenario
    scenarios = SCENARIOS.get(objection_type, [])
    if not scenarios:
        # generic fallback
        soft = ("Понимаю ваш вопрос. Давайте разберёмся и найдём конкретное преимущество." if mode == 'OFFLINE' else
                "Давайте разберёмся и предложим точные цифры по вашей ситуации.")
        firm = ("Цена — важный фактор, но мы покажем вам конкретную экономику по вашим оборотам." if mode == 'OFFLINE' else
                "Мы предоставим точные данные и окупаемость по вашей ситуации.")
        reply_options = [soft, firm]
        best_reply = reply_options[0]
        return {
            "stage": stage,
            "objection_type": objection_type,
            "reply_options": reply_options,
            "tactic": "Уточнить контекст и предложить точные цифры",
            "next_step": "Расчет по вашим данным",
            "best_reply": best_reply,
        }

    # ONLINE mode: try to fetch from OpenAI if API key is provided
    if mode == 'ONLINE':
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            try:
                import openai
                openai.api_key = api_key
                prompt = (
                    f"Client message: {client_message}\n"
                    f"History: {history}\n"
                    f"Return a JSON with keys: stage, objection_type, reply_options (array of 2 strings), tactic, next_step, best_reply."
                )
                resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a senior fintech sales advisor."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600,
                    temperature=0.6,
                )
                content = resp.choices[0].message.get('content', '')
                try:
                    parsed = json.loads(content)
                    required = ["stage", "objection_type", "reply_options", "tactic", "next_step", "best_reply"]
                    if all(k in parsed for k in required):
                        return parsed
                except Exception:
                    pass
            except Exception:
                pass

    # If history repeats the same objection, escalate slightly
    last_objection = None
    for m in reversed(history[-5:]):
        if isinstance(m, dict) and m.get("role") == "manager":
            last_objection = m.get("text")
            break
    escalate = False
    if last_objection and objection_type in last_objection.lower():
        escalate = True

    # Pick a random scenario and two variants
    scenario = random.choice(scenarios)
    soft = scenario.get("soft", "")
    firm = scenario.get("firm", "")
    reply_options = [soft, firm]
    best_reply = firm if escalate else soft if stage in ["сравнение", "интерес"] else firm
    # augment with a simple tactic and next step depending on stage
    tactic = "Address concern with concrete context and offer data."
    if stage == 'уход':
        tactic = "Прямая работа над возражением и предложение альтернатив." 
    next_step = "Предоставить расчеты или примеры как следующем шаге."
    return {
        "stage": stage,
        "objection_type": objection_type,
        "reply_options": reply_options,
        "tactic": tactic,
        "next_step": next_step,
        "best_reply": best_reply,
    }
