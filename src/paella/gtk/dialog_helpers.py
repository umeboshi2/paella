import dialogs



#this needs to be deprecated
def get_single_row(listbox, selected='a row'):
    value = None
    rows = listbox.get_selected_data()
    try:
        value = rows[0]
    except IndexError:
        dialogs.Message('select %s first.' % selected)
        allok = False
    if len(rows) > 1:
        raise Error, 'need to use single select listbox'
    return value

