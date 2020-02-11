def human_read_format(size):
    forms = ['Б', 'КБ', 'МБ', 'ГБ']
    form = 0
    for i in range(3):
        if size > 1023:
            size = size / 1024
            form += 1
    if size * 10 % 10 > 4:
        size += 1
    return str(int(size)) + forms[form]
