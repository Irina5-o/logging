from django import template

register = template.Library()

BAD_WORDS = ["редиска", "некрасивое", "плохое"]

@register.filter(name='censor')
def censor(value):
    if not isinstance(value, str):
        raise ValueError("Фильтр 'censor' применяется только к строкам.")

    words = value.split()
    for i, word in enumerate(words):
        for bad_word in BAD_WORDS:
            if word.lower().startswith(bad_word.lower()):
                words[i] = word[0] + "*" * (len(word) - 1)

    return " ".join(words)