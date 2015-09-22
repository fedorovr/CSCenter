__author__ = 'Roman Fedorov'


def compose(f, g):
    return lambda x: f(g(x))


def constantly(c):
    return lambda *x, **y: c


def flip(func):
    return lambda *x: func(*reversed(x))


def curry(func, *args):
    return lambda *x: func(*args, *x)


def test_part_one():
    f = compose(lambda x: x ** 2, lambda x: x + 1)
    print(f(42))
    g = constantly(42)
    print(g())
    print(g(range(4), range(2), foo="bar"))
    h = flip(map)
    print(list(h(range(10), range(10), lambda x, y: x ** y)))
    print(list(map(lambda x, y: x ** y, range(10), range(10))))
    j = curry(filter, lambda x: x < 5)
    print(list(j(range(10))))
    k = curry(filter, lambda x: x < 5, range(10))
    print(list(k()))


def enumerate(seq, start=0):
    return zip(range(start, start + len(seq)), seq)


def which(pred, seq):
    return map(lambda y: y[0], filter(lambda x: pred(x[1]),
               list(enumerate(seq))))


def all(pred, seq):
    return not list(filter(lambda x: not pred(x), seq))


def any(pred, seq):
    return not all(pred, seq)


def test_part_two():
    print(list(enumerate("abcd")))
    print(list(enumerate("abcd", 1)))
    print(list(which(lambda x: x % 2 == 0, [4, 9, 15])))
    print(all(lambda x: x % 2 == 0, [4, 9, 15]))
    print(all(lambda x: x % 2 == 0, []))
    print(any(lambda x: x % 2 == 0, [4, 9, 15]))
    print(any(lambda x: x % 2 == 0, []))


# Parser :: string -> (tag, result, leftover)
# The goal is to build parser of S-Expressions
OK, ERROR = "OK", "ERROR"


def char(ch):
    def inner(inp):
        if not inp:
            return ERROR, "eof", inp
        elif inp[0] != ch:
            return ERROR, "expected " + ch + " got " + inp[0], inp
        else:
            return OK, ch, inp[1:]
    return inner


def any_of(seq):
    def inner_any(inp):
        if not inp:
            return ERROR, "eof", inp
        elif inp[0] not in seq:
            return ERROR, "expected any of " + seq + " got " + inp[0], inp
        else:
            return OK, inp[0], inp[1:]
    return inner_any


def null_parser(s):
    return OK, [], s


def foldl(foo, acc, list):
    if not list:
        return acc
    else:
        return foldl(foo, foo(acc, list[0]), list[1:])


def combine(acc, parser):
    def sum2(a, b):
        return a + b

    def inner_combine(x):
        tag_acc, result_acc, leftover_acc = acc(x)
        if tag_acc == OK:
            tag_parser, result_parser, leftover_parser = parser(leftover_acc)
            if tag_parser == OK:
                result_acc.append(result_parser)
                return tag_parser, result_acc, leftover_parser
            else:
                return tag_parser, result_parser, \
                       foldl(sum2, "", result_acc) + leftover_parser
        else:
            return tag_acc, result_acc, leftover_acc
    return inner_combine


def chain(*parsers):
    return foldl(combine, null_parser, parsers)


def choice(*parsers):
    def inner_choice(inp):
        for parser in parsers:
            apply = tag, result, leftover = parser(inp)
            if tag == OK:
                return apply
        return ERROR, "none matched", inp
    return inner_choice


def many(parser, empty=True):
    def try_apply_first(inp):
        return try_apply(*null_parser(inp))

    def try_apply(_tag_initial, result_initial, leftover_initial):
        tag, result, leftover = parser(leftover_initial)
        if tag == OK:
            for r in result:
                result_initial.append(r)
            return try_apply(tag, result_initial, leftover)
        else:
            if not(empty or result_initial):
                return tag, result, leftover_initial
            else:
                return OK, result_initial, leftover_initial
    return try_apply_first


def skip(parser):
    def inner_skip(inp):
        parsed = tag, result, leftover = parser(inp)
        return (tag, None, leftover) if tag == OK else parsed
    return inner_skip


def sep_by(parser, separator):
    first = combine(null_parser, parser)
    many_apply = many(combine(combine(null_parser, skip(separator)), parser))

    def not_none(x):
        return x is not None

    def inner_sep_by_first(inp):
        tag_first, result_first, leftover_first = first(inp)
        if tag_first == ERROR:
            return tag_first, result_first, leftover_first
        tag, result, leftover = many_apply(leftover_first)
        return tag, list(filter(not_none, result_first + result)), leftover
    return inner_sep_by_first


def parse(parser, seq):
    tag, result, leftover = parser(seq)
    assert (tag != ERROR) and (not leftover), (result, leftover)
    return result


def transform(p, f):
    def inner(input):
        tag, res, leftover = p(input)
        return tag, f(res) if tag == OK else res, leftover
    return inner


def test_part_three():
    a = any_of("()")
    print(a("("))
    print(a(")"))
    print(a("[]"))
    b = chain(char("("), char(")"))
    print(b("()"))
    print(b("("))
    c = choice(char("."), char("!"))
    print(c("."))
    print(c("!"))
    print(c("?"))
    d = many(char("."))
    print(d("...?!"))
    print(d("."))
    print(d("I have no idea what this is."))
    e = many(char("."), empty=False)
    print(e(".!"))
    print(e("!!"))
    print(e(""))
    f = skip(many(char("."), empty=False))
    print(f("..."))
    print(f(""))
    g = sep_by(any_of("1234567890"), char(","))
    print(g("1,2,3"))
    print(g("1"))
    print(g(""))

    lparen, rparen = skip(char("(")), skip(char(")"))
    ws = skip(many(any_of(" \r\n\t"), empty=False))
    number = transform(many(any_of("1234567890"), empty=False),
                       lambda digits: int("".join(digits)))
    op = any_of("+-*/")

    def sexp(input):
        args = sep_by(choice(number, sexp), ws)
        p = chain(lparen, op, skip(ws), args, rparen)
        p = transform(p, lambda res: (res[1], res[3]))
        return p(input)

    print(parse(sexp, "(+ 42 (* 2 4))"))
