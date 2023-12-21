import math


def parse(data):
    result = list()
    tmp = int()

    for it in data:
        match it:
            case 'i':
                tmp += 1
            case 'd':
                tmp -= 1
            case 's':
                tmp = tmp**2
            case 'o':
                result.append(tmp)
            case _:
                pass

    return [0] if len(result) == 0 else result

# print(parse("codewars"))
# print(parse("ooo"))
# print(parse("ioioio"))
# print(parse("isoisoiso"))
# print(parse('yuyuyu'))


def multiplication_table(size):
    result = list()

    for it in range(1, size + 1):
        result.append([x * it for x in range(1, size + 1)])

    return result

# print(multiplication_table(3))


# String -> N iterations -> String
def fn(s: str, number: int):
    result, c = s, 1

    while number:
        result = result[::2] + result[1::2]
        number -= 1

        if result == s:
            number %= c
        else:
            c += 1

    return result

# must return qtorieuwy
# print(fn('qwertyuio', 2))
# must return Gtsegenri
# print(fn('Greetings', 8))
# must return 159483726
# print(fn('123456789', 8))

# 123456 2

# 135246
# 154326 #

# 123456 3

# 135246
# 154326
# 142536
# 123456 #

# 12345 4

# 13524
# 15432
# 14253
# 12345 #

# 123 2
# 132
# 123 #

def simple_pig_latin(string: str):
    words = list()
    word = ""

    for char in string:
        match char:
            case ' ' | '?' | '!' | '.' | ',' | ':' | ';' | '-':
                if word != '':
                    words.append(word[1:] + word[0] + 'ay' + (char if char != ' ' else ''))
                if char != ' ' and word == '':
                    words.append(char)
                word = ""
            case _:
                word += char

    if word != '':
        words.append(word[1:] + word[0] + 'ay')

    return ' '.join(word for word in words)

# print(simple_pig_latin("Hello, The Best, World! !"))
# print(simple_pig_latin("Pig latin is cool"))

