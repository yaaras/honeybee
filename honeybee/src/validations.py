from yamlfix import fix_code, model

YAMLFIX_CONFIG = model.YamlfixConfig(
    line_length=120,
    sequence_style=model.YamlNodeStyle.KEEP_STYLE,
    explicit_start=False,
    quote_basic_values=True,
)


def run_yamlfix(yaml_text):
    fixed_code = fix_code(yaml_text, config=YAMLFIX_CONFIG)
    return fixed_code
