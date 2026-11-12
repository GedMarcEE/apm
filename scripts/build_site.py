"""Build the Pages catalogue with Python 3.11+ and PyYAML."""
import argparse
import html
import json
from pathlib import Path
import re
import shutil
import yaml

ROOT = Path(__file__).resolve().parents[1]


def frontmatter_description(path):
    text = path.read_text(encoding='utf-8-sig')
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return ''
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == '---'), None)
    if end is None:
        raise ValueError(f'Unclosed frontmatter: {path}')
    metadata = yaml.safe_load('\n'.join(lines[1:end]))
    if not isinstance(metadata, dict):
        raise ValueError(f'Frontmatter must be a mapping: {path}')
    description = metadata.get('description', '')
    if not isinstance(description, str):
        raise ValueError(f'Frontmatter description must be text: {path}')
    return description.strip()


def catalogue(root=ROOT):
    manifest = json.loads((root / 'marketplace.json').read_text(encoding='utf-8'))
    entries = []
    names = set()
    for plugin in manifest['plugins']:
        name = plugin['name']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or name in names:
            raise ValueError(f'Invalid or duplicate package name: {name}')
        names.add(name)
        source = (root / plugin['source']).resolve()
        if not source.is_relative_to(root.resolve()) or not source.is_dir():
            raise ValueError(f'Invalid package source: {source}')
        skill = source / 'SKILL.md'
        prompts = sorted(source.rglob('*.prompt.md'))
        kind = 'skill' if skill.is_file() else 'prompt' if prompts else 'package'
        files = [skill] if skill.is_file() else prompts
        descriptions = [frontmatter_description(p) for p in files]
        description = '\n\n'.join(d for d in descriptions if d) or plugin['description']
        title = ' '.join(word.upper() if word in ('apm', 'ci', 'api', 'cli') else {'github': 'GitHub', 'nodejs': 'Node.js', 'http4k': 'http4k'}.get(word, word.title())
                         for word in name.removeprefix('apm-').split('-'))
        if name in ('apm-pipeline-integration', 'apm-ci-enforcement'):
            title = 'APM ' + title
        if name == 'quarkus-to-guicedee':
            title = 'Quarkus to Guiced'
        entries.append(dict(name=name, title=title,
                            description=description, marketplaceDescription=plugin['description'], category=plugin.get('category', 'General'),
                            kind=kind, source=source.relative_to(root.resolve()).as_posix(),
                            content='\n\n'.join(p.read_text(encoding='utf-8') for p in files)))
    stacks = []
    for path in sorted((root / 'catalogue/stacks').glob('*.json')):
        stack = json.loads(path.read_text(encoding='utf-8'))
        if not all(isinstance(stack.get(k), str) and stack[k] for k in ('name', 'title', 'description')):
            raise ValueError(f'Missing stack metadata: {path}')
        members = stack.get('packages', [])
        if not members or len(set(members)) != len(members) or not set(members) <= names:
            raise ValueError(f'Invalid stack members: {path}')
        if any(s['name'] == stack['name'] for s in stacks):
            raise ValueError(f'Duplicate stack: {path}')
        stacks.append(stack)
    return dict(marketplace=manifest['name'], entries=entries, stacks=stacks)


def build(output):
    data = catalogue()
    output.mkdir(parents=True, exist_ok=True)
    template = (ROOT / 'site/index.html').read_text(encoding='utf-8')
    payload = json.dumps(data, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    fallback = ''.join(f'<li><a href="https://github.com/EqualExperts/apm/tree/main/{html.escape(e["source"], quote=True)}">{html.escape(e["title"])}</a> — {html.escape(e["description"])}</li>' for e in data['entries'])
    (output / 'index.html').write_text(template.replace('__CATALOGUE__', payload).replace('__FALLBACK__', fallback), encoding='utf-8')
    shutil.copyfile(ROOT / 'site/style.css', output / 'style.css')
    shutil.copyfile(ROOT / 'site/selection.css', output / 'selection.css')
    shutil.copyfile(ROOT / '.apm/skills/apm-skill-creator/assets/equal-experts-icon-blue.png', output / 'icon.png')
    (output / '.nojekyll').touch()
    print(f'Built {len(data["entries"])} packages and {len(data["stacks"])} stacks in {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    build(parser.parse_args().output.resolve())
