from django.views.generic import TemplateView


class Extjs4AppView(TemplateView):
    template_name = "extjs4/apptemplate.django.html"
    title = 'ExtJS app'
    css_staticpath = 'extjs4/resources/css/ext-all.css'
    appname = None

    def get(self, request, **kwargs):
        if not self.appname:
            raise ValueError('appname is required')
        return super(Extjs4AppView, self).get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Extjs4AppView, self).get_context_data(**kwargs)
        data = {'title': self.title,
                'css_staticpath': self.css_staticpath,
                'appall_staticpath': '{appname}/app-all.js'.format(appname=self.appname),
                'app_staticpath': '{appname}/app.js'.format(appname=self.appname)}
        context.update(data)
        return data