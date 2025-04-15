def change_names(incidents: list) -> list:
    status_mapping = {
        "open": "В очереди",
        "closed": "Закрыт",
        "resolved": "Решён"
    }
    
    for incident in incidents:
        current_status = incident["status"]
        incident["status"] = status_mapping.get(current_status, current_status)
    
    return incidents

def change_spec(users: list) -> list:
    name_mapping = {
        "user": "Пользователь",
        "admin": "Администратор",
        "system-adm": "Специалист",
        None: "Не назначено"
    }
    
    for user in users:
        current_role = user["role"]
        user["role"] = name_mapping.get(current_role, current_role)
    
    return users

def check_none(users: list) -> list:
    for user in users:
        user["fullname"] = "Не указано" if user["fullname"] is None else user["fullname"]
        user["mail"] = "Не указано" if user["mail"] is None else user["mail"]
    
    return users