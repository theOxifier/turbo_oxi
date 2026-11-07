#!/usr/bin/env python3
"""Build a portable system explorer from a validated JSON model."""
import argparse
import json
from pathlib import Path
from validate_model import load_model, validate

ROOT = Path(__file__).resolve().parent.parent


def render(model):
    errors = validate(model)
    if errors:
        raise ValueError('\n'.join(errors))
    # Never let model text terminate its application/json script element.
    data = json.dumps(model, ensure_ascii=True, allow_nan=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return (ROOT / 'assets' / 'viewer.html').read_text(encoding='utf-8').replace('__MODEL_JSON__', data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.resolve() == args.model.resolve():
        parser.error('output must differ from input model')
    try:
        html = render(load_model(args.model))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(html, encoding='utf-8')
    except (OSError, ValueError) as exc:
        parser.exit(1, f'{exc}\n')
    print(f'Created {args.output}')


if __name__ == '__main__':
    main()
