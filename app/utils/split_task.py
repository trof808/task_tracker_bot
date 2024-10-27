from datetime import datetime

def split_task(text):
    parts = text.rsplit(',', 1)

    if len(parts) == 2:
        task_description = parts[0].strip()
        date_str = parts[1].strip()
        
        try:
            due_date = datetime.strptime(date_str, '%d.%m')
            due_date = due_date.replace(year=datetime.now().year)
            return task_description, due_date
        except ValueError:
            raise ValueError("Invalid date format. Please use 'dd.MM'.")
    else:
        raise ValueError("The input does not contain a valid task and date format.")