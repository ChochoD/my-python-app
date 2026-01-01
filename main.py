import os
from flask import Flask, render_template, jsonify
from datetime import date, timedelta

app = Flask(__name__, template_folder='src')

def get_orthodox_easter(year):
    """Calculates the date of Orthodox Easter for a given year using the Meeus/Butcher algorithm."""
    a = year % 4
    b = year % 7
    c = year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    month = (d + e + 114) // 31
    day = ((d + e + 114) % 31) + 1
    return date(year, month, day) + timedelta(days=13)

def generate_calendar_data(start_year, end_year):
    """Generates the full calendar data including fixed, movable, and fasting dates."""
    calendar_data = []
    month_names_bg = ["Януари", "Февруари", "Март", "Април", "Май", "Юни", "Юли", "Август", "Септември", "Октомври", "Ноември", "Декември"]

    descriptions = {
        # Orthodox Movable
        "easter": "Най-големият празник в православния календар. Чества се възкресението на Исус Христос.",
        "palm_sunday": "Подвижен празник, който се празнува в неделята преди Великден. Отбелязва тържественото влизане на Исус Христос в Йерусалим.",
        "ascension": "Подвижен празник, който се празнува 40 дни след Великден. Отбелязва възнесението на Исус Христос на небето.",
        "pentecost": "Празнува се на 50-ия ден след Великден. На този ден Светият Дух слиза над апостолите.",
        "good_friday": "Денят, в който е разпнат Исус Христос. Строг пост.",
        "holy_saturday": "Последният ден от Страстната седмица. Ден на очакване на Възкресението.",
        "sirni_zagovezni": "Последният ден преди началото на Великия пост. Искаме и даваме прошка.",
        "todorovden": "Празник, посветен на Св. Тодор. Известен с конни надбягвания.",
        "lazarovden": "Подвижен празник, който се отбелязва в съботата преди Цветница. Свързан е с лазаруване.",
        "zadushnica_before_pentecost": "Черешова задушница. Една от големите задушници, в която се почитат починалите.",
        "zadushnica_before_great_lent": "Месопустна задушница. Задушница преди началото на Великия пост.",
        "zadushnica_before_st_michael": "Архангелова задушница. Последната голяма задушница за годината.",
        
        # Orthodox Fixed
        "theophany": "Празник, на който се чества кръщението на Исус Христос в река Йордан. Извършва се ритуал по хвърляне на кръста във вода.",
        "three_holy_hierarchs": "Събор на Св. три светители - Василий Велики, Григорий Богослов и Йоан Златоуст.",
        "annunciation": "Един от 12-те големи християнски празници, на който Архангел Гавриил съобщава на Дева Мария благата вест, че тя ще роди Спасителя.",
        "st_george_orthodox": "Ден на Св. вмчк. Георги Победоносец, един от най-почитаните светци в православието.",
        "sts_cyril_methodius_orthodox": "Ден на светите братя Кирил и Методий, създатели на славянската азбука.",
        "transfiguration": "Един от 12-те големи християнски празници, на който се чества явяването на Исус Христос в божествена светлина пред трима от учениците си.",
        "dormition": "Един от 12-те големи християнски празници, посветен на смъртта (успението) на Божията майка.",
        "nativity_theotokos": "Рождество на Пресвета Богородица. Един от 12-те големи празници.",
        "cross_elevation": "Един от 12-те велики празници. Свързан е с намирането на кръста, на който е бил разпнат Исус Христос.",
        "protection_theotokos": "Покров на Пресвета Богородица, празник на закрилата, която Божията майка дава на вярващите.",
        "st_john_of_rila": "Ден на Св. Йоан Рилски Чудотворец, покровител на българския народ.",
        "presentation_theotokos": "Въведение Богородично. Ден на християнското семейство и младеж.",
        "st_nicholas": "Един от най-почитаните светци в източното православие, покровител на моряците, рибарите и банкерите.",
        "christmas_eve": "На този ден православната църква отбелязва навечерието на Рождество Христово. Традиционно се приготвя постна вечеря с нечетен брой ястия.",

        # Fasting
        "great_lent": "Най-важният и най-продължителният постен период в църковната година. Подготовка за Великден.",
        "apostles_fast": "Петров пост. Пост, установен в памет на светите апостоли Петър и Павел и тяхното дело.",
        "dormition_fast": "Богородичен пост. Двуседмичен пост преди празника Успение Богородично.",
        "nativity_fast": "Рождественски пост. Четиридесетдневен пост преди Рождество Христово.",
        "strict_fast": "Ден на строг пост. Пълно въздържание от храна.",

        # Secular
        "new_year": "Официален почивен ден.",
        "liberation_day": "Национален празник на България.",
        "labor_day": "Международен ден на труда.",
        "st_georges_day_secular": "Ден на храбростта и Българската армия.",
        "cyril_methodius_day_secular": "Ден на българската просвета, култура и на славянската писменост.",
        "unification_day": "Ден на Съединението.",
        "independence_day": "Ден на Независимостта.",
        "non_working": "Официален почивен ден.",

        # Name Days
        "nameday_description": "На този ден празнуват хората, носещи имена, свързани със светеца, който се чества."
    }

    name_days = {
        (1, 1): ["Васил", "Василка", "Веселин", "Веселина", "Весела"],
        (1, 2): ["Силвестър", "Силвия"],
        (1, 6): ["Йордан", "Йорданка", "Данчо", "Богдан", "Богдана", "Богомил", "Найден"],
        (1, 7): ["Иван", "Ивана", "Иванка", "Йоан", "Йоана", "Калоян", "Иво", "Йовко", "Йото", "Ванина", "Жана"],
        (1, 9): ["Юлиян", "Юлияна"],
        (1, 11): ["Богдан", "Теодосий"],
        (1, 12): ["Татяна", "Таня"],
        (1, 14): ["Нина"],
        (1, 17): ["Антон", "Антония", "Андон", "Дончо", "Донка"],
        (1, 18): ["Атанас", "Атанаска", "Наско"],
        (1, 20): ["Евтим", "Евтимия"],
        (1, 21): ["Максим", "Максима"],
        (1, 25): ["Григор", "Григорена"],
        (1, 30): ["Василий", "Григорий", "Йоан"],
        (2, 1): ["Трифон", "Лозан", "Лоза"],
        (2, 3): ["Симеон", "Симона", "Моника"],
        (2, 4): ["Желязко", "Добрин"],
        (2, 6): ["Доротея", "Огнян", "Пламен", "Пламена"],
        (2, 10): ["Харалампи", "Валентин", "Валентина", "Ламби"],
        (2, 13): ["Евлоги"],
        (2, 14): ["Трифон Зарезан"],
        (3, 1): ["Марта", "Мартин", "Мартина"],
        (3, 6): ["Красимир", "Красимира"],
        (3, 9): ["Младен", "Младена"],
        (3, 17): ["Алексей", "Алекси"],
        (3, 22): ["Емил", "Емилия", "Емануил"],
        (3, 24): ["Захари", "Захарина"],
        (3, 25): ["Благовест", "Благовеста", "Благой", "Евангелина"],
        (4, 1): ["Лидия"],
        (4, 6): ["Страхил"],
        (4, 14): ["Мартин"],
        (4, 18): ["Виктор", "Виктория"],
        (4, 25): ["Марк", "Марко"],
        (4, 26): ["Габриела"],
        (5, 2): ["Борис", "Боряна", "Борислава"],
        (5, 5): ["Ирина", "Мирослав", "Мира"],
        (5, 6): ["Георги", "Георгина", "Гергана", "Гинка", "Гоце"],
        (5, 11): ["Кирил", "Кирилка", "Методий", "Методия"],
        (5, 21): ["Константин", "Елена", "Костадин", "Костадинка", "Динко", "Ели"],
        (6, 24): ["Еньо", "Енчо", "Яни", "Яна", "Янко", "Янка", "Дияна", "Диан", "Диана"],
        (6, 29): ["Петър", "Павел", "Петя", "Полина", "Павлина", "Камен"],
        (6, 30): ["Апостол"],
        (7, 1): ["Дамян", "Дамяна"],
        (7, 7): ["Неделя", "Недялко", "Недялка"],
        (7, 15): ["Владимир", "Владислава", "Господин"],
        (7, 16): ["Юлия", "Юлиан"],
        (7, 17): ["Марин", "Марина"],
        (7, 20): ["Илия", "Илияна", "Илко", "Илка"],
        (7, 22): ["Магдалена", "Миглена"],
        (7, 25): ["Анна"],
        (7, 27): ["Пантелей", "Панчо"],
        (8, 8): ["Емилиян"],
        (8, 15): ["Мария", "Мариана", "Марио", "Марияна", "Мара"],
        (8, 20): ["Самуил"],
        (8, 26): ["Адриан", "Адриана", "Наталия"],
        (8, 29): ["Анастас", "Анастасия"],
        (8, 30): ["Александър", "Александра", "Алекс", "Цанко"],
        (9, 1): ["Симеон", "Симона"],
        (9, 5): ["Захари", "Елисавета"],
        (9, 16): ["Людмил", "Людмила"],
        (9, 17): ["София", "Вяра", "Надежда", "Любов", "Любомир", "Любомира"],
        (9, 23): ["Поликсена"],
        (10, 1): ["Покров"],
        (10, 5): ["Игор"],
        (10, 14): ["Петко", "Петка", "Пенчо", "Пенка"],
        (10, 18): ["Злата", "Златина"],
        (10, 19): ["Йоан", "Иван"],
        (10, 26): ["Димитър", "Димитрина", "Димо", "Димка", "Митра"],
        (10, 27): ["Нестор"],
        (11, 4): ["Павел"],
        (11, 8): ["Ангел", "Ангелина", "Михаил", "Михаела", "Рангел", "Райна", "Радко"],
        (11, 11): ["Виктор", "Виктория", "Мина"],
        (11, 14): ["Филип", "Филипа"],
        (11,16): ["Матей"],
        (11, 21): ["Въведение"],
        (11, 24): ["Екатерина", "Катя"],
        (11, 25): ["Климент"],
        (11, 26): ["Стилиян", "Стилияна"],
        (11, 30): ["Андрей", "Андрея"],
        (12, 5): ["Сава", "Савка"],
        (12, 6): ["Никола", "Николай", "Николина", "Нина", "Ненка", "Кольо"],
        (12, 9): ["Анна", "Анка"],
        (12, 17): ["Данаил", "Даниел", "Даниела"],
        (12, 20): ["Игнат", "Огнян", "Пламен"],
        (12, 22): ["Анастасия"],
        (12, 24): ["Евгени", "Евгения", "Жени"],
        (12, 25): ["Христо", "Христина", "Радослав", "Радостина", "Божидар"],
        (12, 26): ["Йосиф", "Давид"],
        (12, 27): ["Стефан", "Стефка", "Стоян", "Стоянка", "Стамен", "Цоньо", "Цонка"]
    }

    fixed_holidays = {
        (1, 1): [{"name": "Нова година", "type": "secular", "description": descriptions["new_year"]}],
        (1, 6): [{"name": "Богоявление (Йордановден)", "type": "orthodox", "description": descriptions["theophany"]}],
        (1, 30): [{"name": "Св. Три Светители", "type": "orthodox", "description": descriptions["three_holy_hierarchs"]}],
        (3, 3): [{"name": "Освобождение на България", "type": "secular", "description": descriptions["liberation_day"]}],
        (3, 25): [{"name": "Благовещение", "type": "orthodox", "description": descriptions["annunciation"]}],
        (5, 1): [{"name": "Ден на труда", "type": "secular", "description": descriptions["labor_day"]}],
        (5, 6): [
            {"name": "Гергьовден, Ден на храбростта", "type": "secular", "description": descriptions["st_georges_day_secular"]},
            {"name": "Св. вмчк. Георги Победоносец", "type": "orthodox", "description": descriptions["st_george_orthodox"]}
        ],
        (5, 24): [
            {"name": "Ден на славянската писменост", "type": "secular", "description": descriptions["cyril_methodius_day_secular"]},
            {"name": "Св. св. Кирил и Методий", "type": "orthodox", "description": descriptions["sts_cyril_methodius_orthodox"]}
        ],
        (8, 6): [{"name": "Преображение Господне", "type": "orthodox", "description": descriptions["transfiguration"]}],
        (8, 15): [{"name": "Успение Богородично", "type": "orthodox", "description": descriptions["dormition"]}],
        (9, 6): [{"name": "Ден на Съединението", "type": "secular", "description": descriptions["unification_day"]}],
        (9, 8): [{"name": "Рождество Богородично", "type": "orthodox", "description": descriptions["nativity_theotokos"]}],
        (9, 14): [{"name": "Въздвижение на Светия Кръст (Кръстовден)", "type": "orthodox", "description": descriptions["cross_elevation"]}],
        (9, 22): [{"name": "Ден на Независимостта", "type": "secular", "description": descriptions["independence_day"]}],
        (10, 1): [{"name": "Покров Богородичен", "type": "orthodox", "description": descriptions["protection_theotokos"]}],
        (10, 19): [{"name": "Св. Йоан Рилски", "type": "orthodox", "description": descriptions["st_john_of_rila"]}],
        (11, 21): [{"name": "Въведение Богородично", "type": "orthodox", "description": descriptions["presentation_theotokos"]}],
        (12, 6): [{"name": "Св. Николай Чудотворец (Никулден)", "type": "orthodox", "description": descriptions["st_nicholas"]}],
        (12, 24): [{"name": "Бъдни вечер", "type": "orthodox", "description": descriptions["christmas_eve"]}],
        (12, 25): [{"name": "Рождество Христово", "type": "orthodox"}],
        (12, 26): [{"name": "Събор на Пресвета Богородица", "type": "orthodox"}]
    }

    non_working_days_fixed = [(1,1), (3,3), (5,1), (5,6), (5,24), (9,6), (9,22), (12,24), (12,25), (12,26)]

    for year in range(start_year, end_year + 1):
        all_events = {}
        easter_date = get_orthodox_easter(year)
        
        # Add movable holidays based on Easter date
        todorovden_offset = (easter_date.weekday() - 5) % 7
        todorovden_date = easter_date - timedelta(days=48 + todorovden_offset)

        # Palm Sunday is the Sunday before Easter
        palm_sunday = easter_date - timedelta(days=7)
        # Lazarovden is the Saturday before Palm Sunday
        lazarovden = palm_sunday - timedelta(days=1)
        
        pentecost_date = easter_date + timedelta(days=49)

        movable_holidays = {
            easter_date - timedelta(days=57): [{"name": "Месопустна задушница", "type": "orthodox", "description": descriptions["zadushnica_before_great_lent"]}],
            easter_date - timedelta(days=49): [{"name": "Сирни заговезни", "type": "orthodox", "description": descriptions["sirni_zagovezni"]}],
            todorovden_date: [{"name": "Тодоровден", "type": "orthodox", "description": descriptions["todorovden"]}],
            lazarovden: [{"name": "Лазаровден", "type": "orthodox", "description": descriptions["lazarovden"]}],
            palm_sunday: [{"name": "Цветница", "type": "orthodox", "description": descriptions["palm_sunday"]}],
            easter_date - timedelta(days=2): [{"name": "Велики петък", "type": "orthodox", "description": descriptions["good_friday"]}],
            easter_date - timedelta(days=1): [{"name": "Велика събота", "type": "orthodox", "description": descriptions["holy_saturday"]}],
            easter_date: [{"name": "ВЕЛИКДЕН", "type": "orthodox", "description": descriptions["easter"]}],
            easter_date + timedelta(days=1): [{"name": "Светли понеделник", "type": "orthodox"}],
            easter_date + timedelta(days=39): [{"name": "Възнесение Господне (Спасовден)", "type": "orthodox", "description": descriptions["ascension"]}],
            pentecost_date - timedelta(days=1): [{"name": "Черешова задушница", "type": "orthodox", "description": descriptions["zadushnica_before_pentecost"]}],
            pentecost_date: [{"name": "Петдесетница", "type": "orthodox", "description": descriptions["pentecost"]}],
        }

        # Add name days for movable holidays
        movable_holidays.setdefault(todorovden_date, []).append({"name": "Имен ден: Тодор, Тодорка, Теодор", "type": "name-day", "description": descriptions["nameday_description"]})
        movable_holidays.setdefault(lazarovden, []).append({"name": "Имен ден: Лазар, Лазарка", "type": "name-day", "description": descriptions["nameday_description"]})
        movable_holidays.setdefault(palm_sunday, []).append({"name": "Имен ден: Цветан, Цветанка, Цветомир, Цветомира, и всички с имена на цветя", "type": "name-day", "description": descriptions["nameday_description"]})
        movable_holidays.setdefault(easter_date + timedelta(days=39), []).append({"name": "Имен ден: Спас, Спаска", "type": "name-day", "description": descriptions["nameday_description"]})

        st_michael_day = date(year, 11, 8)
        zadushnica_st_michael = st_michael_day - timedelta(days=(st_michael_day.weekday() + 2) % 7)
        all_events.setdefault(zadushnica_st_michael, []).extend([{"name": "Архангелова задушница", "type": "orthodox", "description": descriptions["zadushnica_before_st_michael"]}])

        for (month, day), names in name_days.items():
            event = {"name": f"Имен ден: {', '.join(names)}", "type": "name-day", "description": descriptions["nameday_description"]}
            all_events.setdefault(date(year, month, day), []).append(event)

        for (month, day), events in fixed_holidays.items():
            all_events.setdefault(date(year, month, day), []).extend(events)
        for day, events in movable_holidays.items():
            all_events.setdefault(day, []).extend(events)

        non_working_easter = [easter_date - timedelta(days=2), easter_date, easter_date + timedelta(days=1)]
        for day in non_working_easter:
            all_events.setdefault(day, []).append({"name": "Неработен ден", "type": "non-working", "description": descriptions["non_working"]})

        for (month, day) in non_working_days_fixed:
            d = date(year, month, day)
            if not any(e.get('type') == 'non-working' for e in all_events.get(d, [])):
                all_events.setdefault(d, []).append({"name": "Неработен ден", "type": "non-working", "description": descriptions["non_working"]})

        # Add fasting periods
        # Great Lent
        for i in range(48):
            day = easter_date - timedelta(days=48 - i)
            all_events.setdefault(day, []).append({"name": "Велик пост", "type": "fasting", "description": descriptions["great_lent"]})
        
        # Apostles' Fast
        apostles_fast_start = pentecost_date + timedelta(days=8)
        apostles_fast_end = date(year, 6, 28)
        if apostles_fast_start <= apostles_fast_end:
            current_day = apostles_fast_start
            while current_day <= apostles_fast_end:
                all_events.setdefault(current_day, []).append({"name": "Петров пост", "type": "fasting", "description": descriptions["apostles_fast"]})
                current_day += timedelta(days=1)

        # Dormition Fast
        for i in range(15):
            day = date(year, 8, 1) + timedelta(days=i)
            all_events.setdefault(day, []).append({"name": "Богородичен пост", "type": "fasting", "description": descriptions["dormition_fast"]})

        # Nativity Fast
        for i in range(40):
            day = date(year, 11, 15) + timedelta(days=i)
            all_events.setdefault(day, []).append({"name": "Рождественски пост", "type": "fasting", "description": descriptions["nativity_fast"]})

        # Strict fasting days
        all_events.setdefault(date(year, 12, 24), []).append({"name": "Строг пост", "type": "fasting", "description": descriptions["strict_fast"]})
        all_events.setdefault(easter_date - timedelta(days=2), []).append({"name": "Строг пост", "type": "fasting", "description": descriptions["strict_fast"]})
        all_events.setdefault(date(year, 8, 29), []).append({"name": "Строг пост (Отсичане главата на св. Йоан Предтеча)", "type": "fasting", "description": descriptions["strict_fast"]})
        all_events.setdefault(date(year, 9, 14), []).append({"name": "Строг пост (Кръстовден)", "type": "fasting", "description": descriptions["strict_fast"]})


        monthly_data = {f"{month_names_bg[i]} {year}": {"month": f"{month_names_bg[i]} {year}", "days": {}} for i in range(12)}
        for day, events in all_events.items():
            if day.year == year:
                month_key = f"{month_names_bg[day.month - 1]} {day.year}"
                day_key = str(day.day)

                unique_events = []
                added_event_names = set()
                type_priority = ['non-working', 'orthodox', 'secular', 'name-day', 'fasting']
                sorted_events = sorted(events, key=lambda x: type_priority.index(x.get('type', '')) if x.get('type') in type_priority else 99)

                for e in sorted_events:
                    if e['name'] not in added_event_names:
                        unique_events.append(e)
                        added_event_names.add(e['name'])
                monthly_data[month_key]["days"][day_key] = unique_events

        calendar_data.extend(monthly_data.values())

    return sorted(calendar_data, key=lambda x: (int(x['month'].split()[1]), month_names_bg.index(x['month'].split()[0])))

@app.route("/")
def index():
    return render_template('calendar.html')

@app.route("/calendar")
def calendar():
    return render_template('calendar.html')

@app.route("/calendar-data")
def calendar_data():
    data = generate_calendar_data(2024, 2027)
    return jsonify(data)

def main():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    main()
