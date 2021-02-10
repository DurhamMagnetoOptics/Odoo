from odoo import http
class DMOWebManifest(http.Controller):
  manifest_str = """
{
  "background_color": "purple",
  "description": "DMO's Odoo Instance",
  "display": "fullscreen",
  "icons": [
    {
      "src": "/web_enterprise/static/src/img/mobile-icons/android-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ],
  "name": "DMO Odoo",
  "short_name": "Odoo",
  "start_url": "/web"
}  
"""
  sw_string = "self.addEventListener('fetch', (event) => {});"

  @http.route('/web/manifest.webmanifest', auth='public')
  def webmanifest(self):
    return self.manifest_str  

  @http.route('/manifest.webmanifest', auth='public')
  def rootwebmanifest(self):
    return self.webmanifest()  


  @http.route('/web/sw.js', auth='public')
  def webserviceworker(self):
    #see https://stackoverflow.com/questions/56265658/how-provide-a-route-to-download-binary-file-in-odoo-10
    response = http.request.make_response(self.sw_string, headers=[('Content-Type', 'application/javascript')])    
    return response

  @http.route('/sw.js', auth='public')
  def rootserviceworker(self):
    return self.webserviceworker()       