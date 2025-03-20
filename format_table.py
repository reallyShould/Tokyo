def change_names(status: str) -> str:
    status_mapping = {
        "open": "В очереди",
        "closed": "Закрыт",
        "resolved": "Решён"
    }
    return status_mapping[status]