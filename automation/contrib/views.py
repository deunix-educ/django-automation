# encoding: utf-8
import datetime
import os
from io import BytesIO
import zipfile
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
import xhtml2pdf.pisa as pisa


def media_resources(uri, rel):
    return  os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))

class Render:
    @staticmethod
    def render(request, path, params, mode='inline', filename='pdf', cb=None):
        html  = render_to_string(path, params)
        content = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), dest=content, link_callback=media_resources)
        if not pdf.err:
            cf = content.getvalue()
            fp = str(settings.MEDIA_ROOT / f'{filename}.pdf')
            if cb is not None:
                cb(request, fp, cf)
            response = HttpResponse(cf, content_type='application/pdf;')
            response['Content-Disposition'] = '%s; filename=%s-%s.pdf' % (mode, filename, int(datetime.datetime.now().timestamp()), )  
            response['Content-Transfer-Encoding'] = 'binary'          
            return response
        else:
            return HttpResponse("Error Rendering PDF", status=400)


class Export:
    """
    mode in ('inline', 'attachment')
    """
    @staticmethod
    def export_to_csv(resource, queryset=None, mode='attachment', filename='csvfile'):
        try:
            rsrce = resource()
            dataset = rsrce.export(queryset)       
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = '%s; filename="%s-%s.csv"' %(mode, filename, int(datetime.datetime.now().timestamp()), )
            return response
        except Exception as e:
            return HttpResponse("CSV export error %s" % str(e), status=400)
        
    @staticmethod
    def export_to_json(resource, queryset=None, mode='attachment', filename='jsonfile'):
        try:
            rsrce = resource()
            dataset = rsrce.export(queryset)     
            response = HttpResponse(dataset.json, content_type='application/json')
            response['Content-Disposition'] = '%s; filename="%s-%s.json"' %(mode, filename, int(datetime.datetime.now().timestamp()), )
            return response
        except Exception as e:
            return HttpResponse("JSON export error %s" % str(e), status=400)
        
    @staticmethod 
    def export_to_xls(resource, queryset=None, mode='attachment', filename='xlsfile'):
        try:
            rsrce = resource()
            dataset = rsrce.export(queryset)                       
            response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = '%s; filename="%s-%s.xls"' %(mode, filename, int(datetime.datetime.now().timestamp()), )
            return response
        except Exception as e:
            return HttpResponse("XLS export error %s" % str(e), status=400)
        
    @staticmethod 
    def export_zipfile(pathname, files, mode='attachment', filename='zipfile'):   
        try:               
            zip_io = BytesIO()
            with zipfile.ZipFile(zip_io, mode='w') as zip_file:
                for file in files:
                    zip_file.write(os.path.join(pathname, file), arcname=file)

                #response = HttpResponse(zip_io.getvalue(), content_type='application/zip')
                response = HttpResponse(zip_io.getvalue())
                response['Content-Type'] = 'application/x-zip-compressed' 
                response['Content-Disposition'] = '%s; filename="%s-%s.zip"' %(mode, filename, int(datetime.datetime.now().timestamp()), )        
                response['Content-Length'] = zip_io.tell()
                return response
            
        except Exception as e:
            return HttpResponse("ZIP file export error %s" % str(e), status=400)        
   
#
