def get_department(category):

    departments = {

        "Lift": "Maintenance",

        "Network": "IT Department",

        "Water": "Plumbing Department",

        "Power": "Electrical Department",

        "Food": "Food Services",

        "Hostel": "Hostel Administration"
    }

    return departments.get(
        category,
        "General Administration"
    )