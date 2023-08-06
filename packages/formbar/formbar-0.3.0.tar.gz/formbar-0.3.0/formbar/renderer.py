import logging

from mako.lookup import TemplateLookup
from formbar import template_dir

template_lookup = TemplateLookup(directories=[template_dir],
                                 module_directory='/tmp/phormular_modules')

log = logging.getLogger(__name__)


def get_renderer(field, translate):
    """Returns a Renderer. The renderer is choosen based on the
    configured renderer in the field configuration. If no renderer is
    configured the default FormAlchemy-Renderer is returned.

    :field: Field
    :translate: translation function
    :returns: Renderer

    """
    renderer = field._config.renderer
    if renderer is not None:
        # if there is a external Renderer defined for the given renderer
        # type then use this one.
        if field._form.external_renderers.has_key(renderer.render_type):
            return field._form.external_renderers.get(renderer.render_type)(field, translate)
        if renderer.render_type == "textarea":
            return TextareaFieldRenderer(field, translate)
        elif renderer.render_type == "dropdown":
            return DropdownFieldRenderer(field, translate)
    return FAFieldRenderer(field, translate)


class Renderer(object):
    """Basic renderer to render Form objects."""

    def render(self):
        """Returns the rendered element as string

        :returns: Rendered string of the element

        """
        return ""


class FormRenderer(Renderer):
    """Renderer for forms. The renderer will build the the HTML for the
    provided form instance."""

    def __init__(self, form, translate):
        """@todo: to be defined

        :form: @todo
        :translate: Function which return a translated string for a
        given msgid.

        """
        Renderer.__init__(self)

        self._form = form
        self.translate = translate
        self.template = template_lookup.get_template("form.mako")

    def render(self, values={}):
        """Returns the rendered form as string. If values are provided
        these values are used to prefill the form and eventually
        overwrite values in the form.

        :values: dictionary with values which should be used to prefill
        the form.
        :returns: rendered form.

        """
        html = []
        html.append(self._render_form_start())
        html.append(self._render_form_body())
        if not self._form._config.readonly:
            html.append(self._render_form_buttons())
        html.append(self._render_form_end())
        return "".join(html)

    def _render_form_start(self):
        html = []
        html.append('<div class="formbar-form">')
        attr = {'id': self._form._config.id,
                'css': self._form._config.css,
                'action': self._form._config.action,
                'method': self._form._config.method,
                'autocomplete': self._form._config.autocomplete,
                'enctype': self._form._config.enctype,
                '_': self.translate}
        html.append('<form id="%(id)s" class="%(css)s" '
                    'method="%(method)s" action="%(action)s" '
                    'autocomplete="%(autocomplete)s" >' % attr)
        return "".join(html)

    def _render_form_body(self):
        values = {'form': self._form,
                  '_': self.translate}
        return self.template.render(**values)

    def _render_form_buttons(self):
        html = []
        html.append('<div class="row-fluid">')
        html.append('<div class="span12 button-pane well-small">')
        html.append('<button type="submit" '
                    'class="btn btn-primary">%s</button>' % 'Submit')
        html.append('<button type="reset" '
                    'class="btn btn-warning">%s</button>' % 'Reset')
        html.append('</div>')
        html.append('</div>')
        return "".join(html)

    def _render_form_end(self):
        html = []
        html.append('</form>')
        html.append('</div>')
        return "".join(html)


class FieldRenderer(Renderer):
    """Renderer for fields. The renderer will build the the HTML for the
    provided field."""

    def __init__(self, field, translate):
        """Initialize the Renderer with the field instance.

        :field: Field instance

        """
        Renderer.__init__(self)

        self._field = field
        self.translate = translate
        self.template = None

    def _render_label(self):
        template = template_lookup.get_template("label.mako")
        values = {'field': self._field,
                  '_': self.translate}
        return template.render(**values)

    def _render_errors(self):
        template = template_lookup.get_template("errors.mako")
        values = {'field': self._field,
                  '_': self.translate}
        return template.render(**values)

    def _render_help(self):
        template = template_lookup.get_template("help.mako")
        values = {'field': self._field,
                  '_': self.translate}
        return template.render(**values)

    def render(self):
        # TODO: Split rendering in four parts: label, fieldbody, errors,
        # help. Each in its own template.
        html = []
        html.append(self._render_label())
        values = {'field': self._field,
                  '_': self.translate}
        html.append(self.template.render(**values))
        html.append(self._render_errors())
        html.append(self._render_help())
        return "".join(html)


class FAFieldRenderer(FieldRenderer):
    """A Renderer which uses the FormAlchemy renderer configured for the
    FA field in for this field."""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("fa_field.mako")


class TextFieldRenderer(FieldRenderer):
    """A Renderer to render simple fa_field elements"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("fa_field.mako")

class TextareaFieldRenderer(FieldRenderer):
    """A Renderer to render simple fa_field elements"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("textarea.mako")


class PasswordFieldRenderer(FieldRenderer):
    """A Renderer to render passwordfield elements"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("fa_field.mako")


class DropdownFieldRenderer(FieldRenderer):
    """A Renderer to render dropdown list"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("dropdown.mako")


class ListFieldRenderer(FieldRenderer):
    """A Renderer to render selection list"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("fa_field.mako")


class CheckboxFieldRenderer(FieldRenderer):
    """A Renderer to render checkboxes"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("fa_field.mako")


class RadioFieldRenderer(FieldRenderer):
    """A Renderer to render radio boxes"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("fa_field.mako")
