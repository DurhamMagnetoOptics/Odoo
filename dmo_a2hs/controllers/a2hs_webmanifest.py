from odoo import http
class DMOWebManifest(http.Controller):
	@http.route('/web/manifest.webmanifest', auth='public')
	def webmanifest(self):
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
		return manifest_str