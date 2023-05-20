# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class CMSDepartment(models.Model):

    _name = 'cms.department'
    _description = 'Department Information'

    name = fields.Char('Name', required=True)
    parent_id = fields.Many2one(
        'cms.department', string='Main Department', ondelete='restrict', index=True)

    @api.depends('parent_id.parent_path')
    def _compute_parent_path(self):
        for record in self:
            if record.parent_id:
                record.parent_path = '%s/%s' % (
                    record.parent_id.parent_path, record.parent_id.name)
            else:
                record.parent_path = record.name


class CMSGroup(models.Model):
    _name = 'cms.group'
    _description = 'Group Information'

    name = fields.Char("Group Name", required=True)
    group_id = fields.Char("Group ID", required=True)
    # check

    coordinator_id = fields.Many2one('cms.faculty', 'Coordinator')

    student_ids = fields.Many2many(
        "cms.student", 'res_student_group_rel', 'group_id', 'rollno', string='Students', help='Help here')

    _sql_constraints = [
        ('group_id', 'UNIQUE(group_id)',
            'Group ID should be Unique.')]


class CMSProject(models.Model):
    _name = 'cms.project'
    _description = 'Project Information'

    name = fields.Char("Project Title", required=True)
    project_id = fields.Char("Project ID", required=True)
    # check
    description = fields.Char("Description", required=True)
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    remark = fields.Text('Remark')
    group_id = fields.Many2one('cms.group', 'Group')
    attachment_ids = fields.Many2many(
        'ir.attachment', "cms_project_attachment_rel", "project_id", "attachment_id", string='Attachments')

    _sql_constraints = [
        ('project_id', 'UNIQUE(project_id)',
         'Project ID should be Unique.')]


class CMSProjectEvaluation(models.Model):
    _name = "cms.projectevaluation"
    _description = "Evaluation of Project"

    project_id = fields.Many2one('cms.project', 'Project ID')
    group_id = fields.Many2one('cms.group', 'Group')
    faculty_name = fields.Many2one('cms.faculty', 'Faculty')
    # faculty_name = fields.Char(related='faculty.name', string='Faculty Name')
    # check, change name to faculty
    department = fields.Many2one('cms.department', 'Department')
    marks_title = fields.Selection(
        [('proposal', 'Proposal'), ('mid', 'Mid'), ('final', "Final")], 'Marks Title')
    marks_val = fields.Integer(string="Marks Value")
    date = fields.Date(string='Date')
    remark = fields.Text('Remark')
    child_evaluations = fields.One2many(
        'cms.projectevaluation', 'parent_id', string='Project Evaluations')
    parent_id = fields.Many2one(
        'cms.projectevaluation', string='Project Evaluation')

    @api.constrains('proposal_marks')
    def _check_proposal_marks(self):
        for record in self:
            if record.proposal_marks < 0 or record.proposal_marks > 25:
                raise ValidationError(
                    "Proposal marks must be between 0 and 25.")

    @api.constrains('mid_marks')
    def _check_mid_marks(self):
        for record in self:
            if record.mid_marks < 0 or record.mid_marks > 25:
                raise ValidationError("Mid marks must be between 0 and 25.")

    @api.constrains('final_marks')
    def _check_final_marks(self):
        for record in self:
            if record.final_marks < 0 or record.final_marks > 50:
                raise ValidationError("Final marks must be between 0 and 50.")

    def set_to_draft(self):
        '''Method to change state to draft'''
        self.state = 'draft'

    def set_to_verified(self):
        '''Method to change state to verified'''
        self.state = 'verified'

    def set_to_approved(self):
        '''Method to change state to approved'''
        self.state = 'approved'
        self.approved_by = self.env.uid


class CMSStudent(models.Model):

    _name = 'cms.student'                # Internal name of a model
    _description = 'Student Information'

    name = fields.Char('Student Name', required=True)
    rollno = fields.Char("Roll No", required=True)
    father_name = fields.Char('Father Name', required=True)
    admission_no = fields.Char(string='Admission No.', readonly=True)
    registration_no = fields.Char(string='Registration No.')
    admission_date = fields.Datetime('Admission Date', default=date.today())
    birth_date = fields.Date('Date of Birth')
    cnic = fields.Char(string='CNIC')
    phone = fields.Char('Phone no.')
    email = fields.Char('Email')
    cgpa = fields.Float('CGPA')
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')], 'Gender', required=True)
    active = fields.Boolean(default=True, help='Help here')
    image = fields.Binary('Image', widget="image",
                          options={'size': (500, 500)})
    department_id = fields.Many2one('cms.department', 'Department')

    group_ids = fields.Many2many("cms.group", 'res_student_group_rel',
                                 'rollno', 'group_id', string='Groups', help='Help here', readonly=True)

    remark = fields.Text('Remark')
    age = fields.Integer(compute='_compute_student_age',
                         string='Age (Years)', readonly=True)

    _sql_constraints = [
        ('rollno', 'UNIQUE(rollno)',
         'Roll No. should be Unique.'),
        ('admisson_unique', 'UNIQUE(admission_no)',
         'Student Admission No. should be Unique.'),
        ('email_check', "CHECK(position('@' in email) > 0)",
         "Email address must contain '@' symbol")]

    @api.constrains('cnic')
    def _check_cnic_formate(self):
        for rec in self:
            if rec.cnic:
                cnic = str(rec.cnic).strip().replace("-", "")
                if cnic:
                    if len(cnic) != 13:
                        raise ValidationError(
                            _('''Student CNIC should be 13 digits!'''))
                    if not cnic.isdecimal():
                        raise ValidationError(
                            _('''Student CNIC should have valid characters!'''))

    @api.depends('birth_date')
    def _compute_student_age(self):
        '''Method to calculate student age'''
        for rec in self:
            rec.age = 0
            if rec.birth_date:
                today = date.today()
                years = today.year - rec.birth_date.year - \
                    ((today.month, today.day) <
                     (rec.birth_date.month, rec.birth_date.day))
                rec.age = years

        if self.admission_date:
            year = self.admission_date.year

            #self.admission_no  = str(year) + "-" + self.env['ir.sequence'].next_by_code('cms.student.code')
        else:
            raise ValidationError(
                _('Please enter admission date for student %s)', self.name))


class CMSFaculty(models.Model):

    _name = 'cms.faculty'                # Internal name of a model
    # Description, displayed in Odoo user interface
    _description = 'Faculty Information'

    name = fields.Char('Faculty Name', required=True)
    cnic = fields.Char(string='CNIC')
    father_name = fields.Char('Father Name', required=True)
    admission_no = fields.Char(string='Admission No.')
    admission_date = fields.Datetime('Admission Date', default=date.today())
    birth_date = fields.Date('Date of Birth')
    phone = fields.Char('Phone no.')
    email = fields.Char('Email')
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')], 'Gender', required=True)
    active = fields.Boolean(default=True, help='Help here')
    image = fields.Binary('Image', widget="image",
                          options={'size': (500, 500)})
    department_id = fields.Many2one('cms.department', 'Department')
    remark = fields.Text('Remark')
    age = fields.Integer(compute='_compute_faculty_age',
                         string='Age (Years)', readonly=True)

    parent_id = fields.Many2one(
        'cms.faculty', string='Main Faculty', ondelete='restrict', index=True)

    @api.depends('parent_id.parent_path')
    def _compute_parent_path(self):
        for record in self:
            if record.parent_id:
                record.parent_path = '%s/%s' % (
                    record.parent_id.parent_path, record.parent_id.name)
            else:
                record.parent_path = record.name

    _sql_constraints = [
        ('admisson_unique', 'UNIQUE(admission_no)',
         'Faculty Admission No. should be Unique.'),
        ('email_check', "CHECK(position('@' in email) > 0)",
         "Email address must contain '@' symbol")]

    @api.constrains('cnic')
    def _check_cnic_formate(self):
        for rec in self:
            if rec.cnic:
                cnic = str(rec.cnic).strip().replace("-", "")
                if cnic:
                    if len(cnic) != 13:
                        raise ValidationError(
                            _('''Faculty CNIC should be 13 digits!'''))
                    if not cnic.isdecimal():
                        raise ValidationError(
                            _('''Faculty CNIC should have valid characters!'''))

    @api.depends('birth_date')
    def _compute_faculty_age(self):
        '''Method to calculate Faculty age'''
        for rec in self:
            rec.age = 0
            if rec.birth_date:
                today = date.today()
                years = today.year - rec.birth_date.year - \
                    ((today.month, today.day) <
                     (rec.birth_date.month, rec.birth_date.day))
                rec.age = years
