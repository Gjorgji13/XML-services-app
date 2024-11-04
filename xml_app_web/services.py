def get_user_data(user_id):
    # Simulated user database
    mock_database = {
        '1': {'Name': 'Alice', 'Age': '30'},
        '2': {'Name': 'Bob', 'Age': '25'},
        '3': {'Name': 'Charlie', 'Age': '35'},
    }
    return mock_database.get(user_id, None)
