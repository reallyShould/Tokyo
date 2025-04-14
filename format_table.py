def change_names(status: str) -> str:
    status_mapping = {
        "open": "В очереди",
        "closed": "Закрыт",
        "resolved": "Решён"
    }
    return status_mapping[status]

def change_spec(name: str) -> str:
    name_mapping = {
        "user":"Пользователь",
        "admin":"Администратор",
        "system-adm":"Специалист",
        None:"Не назначено"
    }
    return name_mapping[name]

def check_none(text: str) -> str:
    if text == None:
        return "Не указано"
    else:
        return text