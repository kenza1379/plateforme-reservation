from django import template

register = template.Library()

@register.filter
def split_by(value, separator=','):
    """
    Coupe une chaîne de texte en liste selon le séparateur donné.
    Exemple : "Wi-Fi, Projecteur" → ["Wi-Fi", "Projecteur"]
    """
    if value:
        return [v.strip() for v in value.split(separator)]
    return []
