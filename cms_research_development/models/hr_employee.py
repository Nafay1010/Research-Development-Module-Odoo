from odoo import models, fields, api, _
from datetime import date
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.api import ondelete

class HrEmployee(models.Model):
    _inherit = "hr.employee"
    
    is_faculty = fields.Boolean("Is Faculty")
    is_visiting = fields.Boolean("Is Visiting")

class EventOrganizer(models.Model):
    _name = "event.organizer"
    _inherit = "hr.employee"
    _description = "Organizer Class"
    
    is_organizer = fields.Boolean("Is Organizer")
    category_ids = fields.Many2many('hr.employee.category', 'organizer_category_rel',
        'emp_id', 'category_id', groups="hr.group_hr_user",
        string='Tags')
    

class HrEmployeeOrganizer(models.Model):
    _name = "hr.employee.organizer"
    
    _inherits = {"hr.employee": "parent_id"}
    _description = "Employee Organizer Class"
    
    success_rate = fields.Float("Success rate")
    parent_id = fields.Many2one("hr.employee", "Parent ID", required=True, ondelete="cascade")
    
    
