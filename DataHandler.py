import requests


class DataHandler:
    api_url = "http://progetti.altervista.org/orari/botServer/api.php"

    @staticmethod
    def __add_quotes(string):
        return "'" + string + "'"

    @staticmethod
    def get_years():
        url = "http://westcost0.altervista.org/orari/api.php?w=getyears"
        response = requests.get(url).json()
        return response

    @staticmethod
    def get_courses(year):
        url = "http://westcost0.altervista.org/orari/api.php?w=getcourses"
        response = requests.get(url, {"year": year}).json()
        return response

    @staticmethod
    def get_timetable(uid):
        response = requests.get(DataHandler.api_url, {"uid": uid}).json()
        return response

    @staticmethod
    def set_year(year, uid):
        requests.post(DataHandler.api_url, {"uid": uid, "year": year})

    @staticmethod
    def set_course(course, uid):
        requests.post(DataHandler.api_url, {"uid": uid, "course": DataHandler.__add_quotes(course)})

    @staticmethod
    def set_year2(year2, uid):
        requests.post(DataHandler.api_url, {"uid": uid, "year2": DataHandler.__add_quotes(year2)})

    @staticmethod
    def set_txt_curr(txt_curr, uid):
        requests.post(DataHandler.api_url, {"uid": uid, "txt_curr": DataHandler.__add_quotes(txt_curr)})

    @staticmethod
    def set_uid(uid):
        requests.post(DataHandler.api_url, {"uid": uid})
