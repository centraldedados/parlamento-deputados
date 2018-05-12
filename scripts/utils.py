def replace_letters(s, letters, l):
    '''Replace all specified characters with a substring.'''
    for letter in letters:
        s = s.replace(letter, l)
    return s


def slugify(s):
    '''Creates accent-aware slugs based on human formatted strings.'''
    s = s.strip()
    s = s.lower()
    s = s.replace("-", "")
    s = s.replace(" ", "-")
    s = s.replace("'", "-")
    s = replace_letters(s, u"áàâã", u"a")
    s = replace_letters(s, u"éèê", u"e")
    s = replace_letters(s, u"íì", u"i")
    s = replace_letters(s, u"óòôõ", u"o")
    s = replace_letters(s, u"úù", u"u")
    s = replace_letters(s, u"ç", u"c")
    return s


def lower_given_name(txt):
    # transforma um nome em maiúsculas ("WANDA D'AZEVEDO GUIMARÃES")
    # numa versão corretamente capitalizada ("Wanda d'Azevedo Guimarães")
    newtxt = ""

    # caso especial em que "D'" e o nome seguinte são palavras separadas
    if " D' " in txt:
        txt = txt.replace(" D' ", " D'")

    # vamos capitalizar palavra a palavra
    for word in txt.split(" "):
        word = word.lower()
        if word.startswith("d'"):
            # capitalizar corretamente "d'Azevedo" e semelhantes
            word = word[:2] + word[2].upper() + word[3:]
        elif word.startswith(('d', 'e')) and len(word) <= 3:
            # "e", "da", "de", "dos", etc
            pass
        else:
            # capitalização normal
            word = word.title()
        newtxt += word + " "
    return newtxt.strip()
