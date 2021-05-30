from flask import render_template
from app import app, mysql

class City(object):
    def __init__(self, name):
        self.name = name
        self.count = 0
        self.number = 0
        self.people = []
    def add_person(self, name, surname, email):
        self.count += 1
        self.people.append([name, surname, email])

class State(object):
    def __init__(self, name):
        self.name = name
        self.cities = []
        self.city_count = 0
    def add_city(self, name):
        if self.cities and self.cities[-1].count < 2:
            self.cities.pop()
            self.city_count -= 1
        self.city_count += 1
        self.cities.append(City(name))
    def add_person(self, name, surname, email):
        self.cities[-1].add_person(name, surname, email)

def prepare_data(data):
    res = []
    curr_state = ''
    curr_city = ''
    def check_last_state(res):
        if res and res[-1].cities[-1].count < 2:
                res[-1].cities.pop()
                res[-1].city_count -= 1
        if res and res[-1].city_count == 0:
            res.pop()
    for person in data:
        first_name, last_name, city, state, email = person
        if state != curr_state:
            check_last_state(res)
            res.append(State(state))
            curr_city = ''
            curr_state = state
        if city != curr_city:
            res[-1].add_city(city)
            curr_city = city
        res[-1].add_person(first_name, last_name, email)
    check_last_state(res)
    for state in res:
        nr = 0
        state.cities = sorted(state.cities, key=lambda city : city.count, reverse=True)
        for city in state.cities:
            nr += 1
            city.number = nr
    return res


@app.route('/')
@app.route('/index')
def index():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT first_name, last_name, city, state, email FROM addresses ORDER BY state, city, first_name, last_name;''')
    data = cursor.fetchall()
    return render_template('index.html', data = prepare_data(data))