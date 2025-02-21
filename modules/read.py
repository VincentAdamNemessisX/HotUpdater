def read_data():
    with open("stg/data.txt", "r") as f:
        data = f.read()
    return f"Processed: {data}"
