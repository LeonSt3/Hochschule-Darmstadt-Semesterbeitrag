import matplotlib.pyplot as plt

data = {
    "Sommersemester 2008": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2008/2009": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2009": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2009/2010": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2010": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2010/2011": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2011": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2011/2012": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2012": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2012/2013": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2013": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2013/2014": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2014": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2014/2015": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2015": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2015/2016": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2016": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2016/2017": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2017": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2017/2018": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2018": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2018/2019": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2019": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2019/2020": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2020": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2020/2021": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2021": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2021/2022": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2022": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2022/2023": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2023": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2023/2024": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2024": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2024/2025": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2025": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Wintersemester 2025/2026": {
        "Studierendenwerksbeitrag": None,
        "Kulturticket": None,
        "Studierendenschaftsbeitrag": None,
        "Verwaltungskostenbeitrag": None,
        "Bundesweites Semesterticket": None,
        "Leihfahrradsystem": None,
    },
    "Sommersemester 2026": {
        "Studierendenwerksbeitrag": 103.00,
        "Kulturticket": 2.71,
        "Studierendenschaftsbeitrag": 15.51,
        "Verwaltungskostenbeitrag": 50.00,
        "Bundesweites Semesterticket": 208.80,
        "Leihfahrradsystem": 2.98,
    },
}

# filter semesters that already have numbers
semesters = []
components = []
stack_values = {}

for sem, comps in data.items():
    if None in comps.values():
        continue
    semesters.append(sem)

    if not components:
        components = list(comps.keys())
        stack_values = {c: [] for c in components}

    for c in components:
        stack_values[c].append(comps[c])

if semesters:
    bottom = [0] * len(semesters)
    plt.figure(figsize=(10, 5))

    for comp in components:
        plt.bar(semesters, stack_values[comp], bottom=bottom)
        bottom = [bottom[i] + stack_values[comp][i] for i in range(len(bottom))]

    plt.xticks(rotation=20, ha="right")
    plt.ylabel("Euro")
    plt.title("Zusammensetzung Semesterbeitrag")
    plt.tight_layout()
    plt.show()
else:
    print("No semesters contain values yet.")
