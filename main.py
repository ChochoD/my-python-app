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
        "annunciation": "Един от 12-те големи християнски празници, на който Архангел Гавриил съобщава на Дева Мария благата вест, че тя ще роди Спасителя.",
        "transfiguration": "Един от 12-те големи християнски празници, на който се чества явяването на Исус Христос в божествена светлина пред трима от учениците си.",
        "dormition": "Един от 12-те големи християнски празници, посветен на смъртта (успението) на Божията майка.",
        "cross_elevation": "Един от 12-те велики празници. Свързан е с намирането на кръста, на който е бил разпнат Исус Христос.",
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
        "st_georges_day": "Ден на храбростта и Българската армия.",
        "cyril_methodius_day": "Ден на славянската писменост и култура.",
        "unification_day": "Ден на Съединението.",
        "independence_day": "Ден на Независимостта.",
        "non_working": "Официален почивен ден."
    }

    fixed_holidays = {
        (1, 1): [{"name": "Нова година", "type": "secular", "description": descriptions["new_year"]}],
        (1, 6): [{"name": "Богоявление (Йордановден)", "type": "orthodox", "description": descriptions["theophany"]}],
        (3, 3): [{"name": "Освобождение на България", "type": "secular", "description": descriptions["liberation_day"]}],
        (3, 25): [{"name": "Благовещение", "type": "orthodox", "description": descriptions["annunciation"]}],
        (5, 1): [{"name": "Ден на труда", "type": "secular", "description": descriptions["labor_day"]}],
        (5, 6): [{"name": "Гергьовден", "type": "secular", "description": descriptions["st_georges_day"]}],
        (5, 24): [{"name": "Ден на славянската писменост", "type": "secular", "description": descriptions["cyril_methodius_day"]}],
        (8, 6): [{"name": "Преображение Господне", "type": "orthodox", "description": descriptions["transfiguration"]}],
        (8, 15): [{"name": "Успение Богородично", "type": "orthodox", "description": descriptions["dormition"]}],
        (9, 6): [{"name": "Ден на Съединението", "type": "secular", "description": descriptions["unification_day"]}],
        (9, 14): [{"name": "Въздвижение на Светия Кръст (Кръстовден)", "type": "orthodox", "description": descriptions["cross_elevation"]}],
        (9, 22): [{"name": "Ден на Независимостта", "type": "secular", "description": descriptions["independence_day"]}],
        (12, 6): [{"name": "Св. Николай Чудотворец (Никулден)", "type": "orthodox", "description": descriptions["st_nicholas"]}],
        (12, 24): [{"name": "Бъдни вечер", "type": "orthodox", "description": descriptions["christmas_eve"]}],
        (12, 25): [{"name": "Рождество Христово", "type": "orthodox"}],
        (12, 26): [{"name": "Събор на Пресвета Богородица", "type": "orthodox"}]
    }

    non_working_days_fixed = [(1,1), (3,3), (5,1), (5,6), (5,24), (9,6), (9,22), (12,24), (12,25), (12,26)]

    for year in range(start_year, end_year + 1):
        all_events = {}
        easter_date = get_orthodox_easter(year)
        pentecost_date = easter_date + timedelta(days=49)

        movable_holidays = {
            easter_date - timedelta(days=57): [{"name": "Месопустна задушница", "type": "orthodox", "description": descriptions["zadushnica_before_great_lent"]}],
            easter_date - timedelta(days=49): [{"name": "Сирни заговезни", "type": "orthodox", "description": descriptions["sirni_zagovezni"]}],
            easter_date - timedelta(days=42): [{"name": "Тодоровден", "type": "orthodox", "description": descriptions["todorovden"]}],
            easter_date - timedelta(days=8): [{"name": "Лазаровден", "type": "orthodox", "description": descriptions["lazarovden"]}],
            easter_date - timedelta(days=7): [{"name": "Цветница", "type": "orthodox", "description": descriptions["palm_sunday"]}],
            easter_date - timedelta(days=2): [{"name": "Велики петък", "type": "orthodox", "description": descriptions["good_friday"]}],
            easter_date - timedelta(days=1): [{"name": "Велика събота", "type": "orthodox", "description": descriptions["holy_saturday"]}],
            easter_date: [{"name": "ВЕЛИКДЕН", "type": "orthodox", "description": descriptions["easter"]}],
            easter_date + timedelta(days=1): [{"name": "Светли понеделник", "type": "orthodox"}],
            easter_date + timedelta(days=39): [{"name": "Възнесение Господне", "type": "orthodox", "description": descriptions["ascension"]}],
            pentecost_date - timedelta(days=1): [{"name": "Черешова задушница", "type": "orthodox", "description": descriptions["zadushnica_before_pentecost"]}],
            pentecost_date: [{"name": "Петдесетница", "type": "orthodox", "description": descriptions["pentecost"]}],
        }
        
        st_michael_day = date(year, 11, 8)
        zadushnica_st_michael = st_michael_day - timedelta(days=(st_michael_day.weekday() + 2) % 7)
        all_events.setdefault(zadushnica_st_michael, []).extend([{"name": "Архангелова задушница", "type": "orthodox", "description": descriptions["zadushnica_before_st_michael"]}])

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
            day = easter_date - timedelta(days=47 - i)
            all_events.setdefault(day, []).append({"name": "Велик пост", "type": "fasting", "description": descriptions["great_lent"]})
        
        # Apostles' Fast
        apostles_fast_start = pentecost_date + timedelta(days=8) # Starts on Monday after All Saints' Sunday
        apostles_fast_end = date(year, 6, 28)
        if apostles_fast_start <= apostles_fast_end:
            for i in range((apostles_fast_end - apostles_fast_start).days + 1):
                day = apostles_fast_start + timedelta(days=i)
                all_events.setdefault(day, []).append({"name": "Петров пост", "type": "fasting", "description": descriptions["apostles_fast"]})

        # Dormition Fast
        for i in range(14):
            day = date(year, 8, 1) + timedelta(days=i)
            all_events.setdefault(day, []).append({"name": "Богородичен пост", "type": "fasting", "description": descriptions["dormition_fast"]})

        # Nativity Fast
        for i in range(40):
            day = date(year, 11, 15) + timedelta(days=i)
            all_events.setdefault(day, []).append({"name": "Рождественски пост", "type": "fasting", "description": descriptions["nativity_fast"]})

        # Strict fasting days
        all_events.setdefault(date(year, 12, 24), []).append({"name": "Строг пост", "type": "fasting", "description": descriptions["strict_fast"]})
        all_events.setdefault(easter_date - timedelta(days=2), []).append({"name": "Строг пост", "type": "fasting", "description": descriptions["strict_fast"]})

        monthly_data = {f"{month_names_bg[i]} {year}": {"month": f"{month_names_bg[i]} {year}", "days": {}} for i in range(12)}
        for day, events in all_events.items():
            month_key = f"{month_names_bg[day.month - 1]} {day.year}"
            day_key = str(day.day)

            unique_events = []
            added_event_names = set()
            for e in sorted(events, key=lambda x: x.get('type', '')):
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
