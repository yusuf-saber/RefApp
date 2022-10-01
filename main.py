# Imports
from flask import Flask, render_template
import contentful
import markdown
import markdown.extensions.fenced_code
import markdown.extensions.codehilite
from dotenv import load_dotenv
import os

# Create Flask App
app = Flask(__name__)

# Load Creds
load_dotenv()

# Connect to Contentful
space_id = os.environ.get('CONTENTFUL_SPACE_ID')
access_token = os.environ.get('CONTENTFUL_ACCESS_TOKEN')
client = contentful.Client(space_id, access_token)


def get_disciplines():
    disciplines = client.entries({'content_type': 'discipline'})
    # TODO: Return sorted
    return disciplines


def get_default_discipline():
    default_discipline = client.entries({'content_type': 'discipline', 'fields.order': '1'})[0]
    return default_discipline


def get_discipline(discipline_slug):
    discipline = client.entries({'content_type': 'discipline', 'fields.slug': discipline_slug})[0]
    return discipline


def get_languages(discipline):
    languages = discipline.languages
    languages.sort(key=lambda x: x.order, reverse=False)
    return languages


def get_default_language(languages):
    default_language = languages[0]
    return default_language


def get_language(language_slug):
    language = client.entries({'content_type': 'language', 'fields.slug': language_slug})[0]
    return language


def get_nodes():
    nodes = client.entries({'content_type': 'node'})
    return nodes


def get_root_node(nodes, discipline):
    root = nodes[0]
    for node in nodes:
        if node.id == discipline.root.id:
            root = node
    return root


def get_node(node_slug):
    node = client.entries({'content_type': 'node', 'fields.slug': node_slug})[0]
    return node


def get_node_path_helper(current_path, current_root_node, current_node):
    path = []
    if hasattr(current_root_node, 'children'):
        if any(node.id == current_node.id for node in current_root_node.children):
            return current_path + [current_root_node, current_node]
        else:
            current_path = current_path + [current_root_node]
            for node in current_root_node.children:
                path = get_node_path_helper(current_path, node, current_node)
                if len(path) > 0:
                    break
            return path
    else:
        return path


def get_node_path(root_node, current_node):
    node_path = get_node_path_helper([], root_node, current_node)
    return node_path


def get_piece(language_slug, node_slug):
    response = client.entries({
        'content_type': 'piece',
        'fields.language.sys.contentType.sys.id': 'language',
        'fields.language.fields.slug': language_slug,
        'fields.node.sys.contentType.sys.id': 'node',
        'fields.node.fields.slug': node_slug
    })
    return response[0]


def to_html(piece_body_markdown):
    piece_body_html = markdown.markdown(
        piece_body_markdown, extensions=["fenced_code"]
        # ["fenced_code", "codehilite"]
    )
    return piece_body_html


@app.route('/')
@app.route('/<discipline_slug>')
def disciplines():
    # Query data
    disciplines = get_disciplines()
    current_discipline = get_default_discipline()
    languages = get_languages(current_discipline)
    current_language = get_default_language(languages)
    nodes = get_nodes()
    root_node = get_root_node(nodes, current_discipline)
    current_node = root_node
    current_piece = get_piece(current_language.slug, current_node.slug)
    current_piece_body_html = to_html(current_piece.body)
    # Render template
    return render_template('index.html',
                           disciplines=disciplines,
                           current_discipline=current_discipline,
                           languages=languages,
                           current_language=current_language,
                           root_node=root_node,
                           current_node=current_node,
                           current_piece_body_html=current_piece_body_html)


@app.route('/<discipline_slug>/<language_slug>')
def language(discipline_slug=None, language_slug=None):
    # Query data
    disciplines = get_disciplines()
    current_discipline = get_discipline(discipline_slug)
    languages = get_languages(current_discipline)
    current_language = get_language(language_slug)
    categories = get_nodes()
    root_node = get_root_node(categories, current_discipline)
    current_node = root_node
    current_piece = get_piece(current_language.slug, current_node.slug)
    current_piece_body_html = to_html(current_piece.body)
    # Render template
    return render_template('index.html',
                           disciplines=disciplines,
                           current_discipline=current_discipline,
                           languages=languages,
                           current_language=current_language,
                           root_node=root_node,
                           current_node=current_node,
                           current_piece_body_html=current_piece_body_html)


@app.route('/<discipline_slug>/<language_slug>/<node_slug>')
def piece(discipline_slug=None, language_slug=None, node_slug=None):
    # Query data
    disciplines = get_disciplines()
    current_discipline = get_discipline(discipline_slug)
    languages = get_languages(current_discipline)
    current_language = get_language(language_slug)
    categories = get_nodes()
    root_node = get_root_node(categories, current_discipline)
    current_node = get_node(node_slug)
    node_path = get_node_path(root_node, current_node)
    current_piece = get_piece(current_language.slug, current_node.slug)
    current_piece_body_html = to_html(current_piece.body)
    # Render template
    return render_template('index.html',
                           disciplines=disciplines,
                           current_discipline=current_discipline,
                           languages=languages,
                           current_language=current_language,
                           root_node=root_node,
                           current_node=current_node,
                           node_path=node_path,
                           current_piece_body_html=current_piece_body_html,
                           current_piece_title=current_piece.title)


if __name__ == '__main__':
    app.run()
