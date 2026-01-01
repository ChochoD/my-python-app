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
        "easter": "Най-големият празник в православния календар. Чества се възкресението на Исус Христос.",
        "palm_sunday": "Подвижен празник, който се празнува в неделята преди Великден. Отбелязва тържественото влизане на Исус Христос в Йерусалим.",
        "ascension": "Подвижен празник, който се празнува 40 дни след Великден. Отбелязва възнесението на Исус Христос на небето.",
        "pentecost": "Празнува се на 50-ия ден след Великден. На този ден Светият Дух слиза над апостолите.",
        "good_friday": "Денят, в който е разпнат Исус Христос. Строг пост.",
        "holy_saturday": "Последният ден от Страстната седмица. Ден на очакване на Възкресението.",
        "great_lent": "Най-важният и най-продължителният постен период в църковната година. Подготовка за Великден.",
        "nativity_fast": "Рождественски пост. Четиридесетдневен пост преди Рождество Христово.",
        "christmas_eve": "На този ден православната църква отбелязва навечерието на Рождество Христово. Традиционно се приготвя постна вечеря с нечетен брой ястия.",
        "new_year": "Официален почивен ден.",
        "liberation_day": "Национален празник на България.",
        "labor_day": "Международен ден на труда.",
        "st_georges_day": "Ден на храбростта и Българската армия.",
        "cyril_methodius_day": "Ден на славянската писменост и култура.",
        "unification_day": "Ден на Съединението.",
        "independence_day": "Ден на Независимостта.",
        "non_working": "Официален почивен ден.",
        "strict_fast": "Ден на строг пост. Пълно въздържание от храна."
    }

    fixed_holidays = {
        (1, 1): [{"name": "Нова година", "type": "secular", "description": descriptions["new_year"]}],
        (3, 3): [{"name": "Освобождение на България", "type": "secular", "description": descriptions["liberation_day"]}],
        (5, 1): [{"name": "Ден на труда", "type": "secular", "description": descriptions["labor_day"]}],
        (5, 6): [{"name": "Гергьовден", "type": "secular", "description": descriptions["st_georges_day"]}],
        (5, 24): [{"name": "Ден на славянската писменост", "type": "secular", "description": descriptions["cyril_methodius_day"]}],
        (9, 6): [{"name": "Ден на Съединението", "type": "secular", "description": descriptions["unification_day"]}],
        (9, 22): [{"name": "Ден на Независимостта", "type": "secular", "description": descriptions["independence_day"]}],
        (12, 24): [{"name": "Бъдни вечер", "type": "orthodox", "description": descriptions["christmas_eve"]}],
        (12, 25): [{"name": "Рождество Христово", "type": "orthodox"}],
        (12, 26): [{"name": "Събор на Пресвета Богородица", "type": "orthodox"}]
    }

    for year in range(start_year, end_year + 1):
        all_events = {}
        easter_date = get_orthodox_easter(year)

        movable_holidays = {
            easter_date - timedelta(days=48): [{"name": "Начало на Великия пост", "type": "orthodox"}],
            easter_date - timedelta(days=7): [{"name": "Цветница", "type": "orthodox", "description": descriptions["palm_sunday"]}],
            easter_date - timedelta(days=2): [{"name": "Велики петък", "type": "orthodox", "description": descriptions["good_friday"]}],
            easter_date - timedelta(days=1): [{"name": "Велика събота", "type": "orthodox", "description": descriptions["holy_saturday"]}],
            easter_date: [{"name": "ВЕЛИКДЕН", "type": "orthodox", "description": descriptions["easter"]}],
            easter_date + timedelta(days=1): [{"name": "Светли понеделник", "type": "orthodox"}],
            easter_date + timedelta(days=39): [{"name": "Възнесение Господне", "type": "orthodox", "description": descriptions["ascension"]}],
            easter_date + timedelta(days=49): [{"name": "Петдесетница", "type": "orthodox", "description": descriptions["pentecost"]}],
        }

        # Add fixed and movable holidays to all_events
        for (month, day), events in fixed_holidays.items():
            all_events.setdefault(date(year, month, day), []).extend(events)
        for day, events in movable_holidays.items():
            all_events.setdefault(day, []).extend(events)

        # Add fasting periods
        # Great Lent
        for i in range(48):
            day = easter_date - timedelta(days=48-i)
            all_events.setdefault(day, []).append({"name": "Велик пост", "type": "fasting", "description": descriptions["great_lent"]})
        # Nativity Fast
        for i in range(40):
            day = date(year, 11, 15) + timedelta(days=i)
            all_events.setdefault(day, []).append({"name": "Рождественски пост", "type": "fasting", "description": descriptions["nativity_fast"]})

        # Strict fasting days
        all_events.setdefault(date(year, 12, 24), []).append({"name": "Строг пост", "type": "fasting", "description": descriptions["strict_fast"]})
        all_events.setdefault(easter_date - timedelta(days=2), []).append({"name": "Строг пост", "type": "fasting", "description": descriptions["strict_fast"]})

        # Format data for JSON output
        monthly_data = {f"{month_names_bg[i]} {year}": {"month": f"{month_names_bg[i]} {year}", "days": {}} for i in range(12)}
        for day, events in all_events.items():
            month_key = f"{month_names_bg[day.month-1]} {day.year}"
            day_key = str(day.day)
            # Filter out duplicate fasting events
            unique_events = []
            fasting_added = False
            for e in sorted(events, key=lambda x: x['type'], reverse=True):
                if e['type'] == 'fasting':
                    if not fasting_added:
                        unique_events.append(e)
                        fasting_added = True
                else:
                    unique_events.append(e)
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
