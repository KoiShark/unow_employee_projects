/** @odoo-module **/

import publicWidget from 'web.public.widget';
import rpc from 'web.rpc';

publicWidget.registry.EmployeeProjectPortal = publicWidget.Widget.extend({
    selector: '.o_employee_project_portal',
    events: {
        'click .create-project': '_onOpenModal',
        'click #save-project': '_onSaveProject',
    },

    init: function (parent, options) {
        this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------
    _onOpenModal: async function (ev) {
        const currentElement = $(ev.currentTarget);
        const currentEmployee = parseInt(currentElement.attr('current_employee'))
        const employeeSelect = $('select#employee');
        const fields = ['id', 'name'];
        const domain = [];
        let optionTags = `<option value="" disabled="1">Select an employee</option>`
        try {
            // Get values for available employees
            const employeeIds = await rpc.query({
                model: 'hr.employee',
                method: 'search_read',
                kwargs: {
                    fields: fields,
                    domain: domain,
                }
            });
            if (employeeIds) {
                employeeIds.forEach(element => {
                    if (element.id === currentEmployee) {
                        optionTags += `
                            <option
                                value="${element.id}"
                                selected="1"
                            >
                            ${element.name}
                            </option>`
                    } else {
                        optionTags += `
                            <option
                                value="${element.id}"
                            >
                            ${element.name}
                            </option>`
                    }
                });
            };

            // append options to selection tag
            employeeSelect.html(optionTags)

        } catch (error) {
            console.error(error);
        };
    },
    _onSaveProject: async function createEmployeeProject() {
        // Method to communicate with controller and handle creation
        const projectName = $('#name').val(); // Input for project name
        const employeeId = $('#employee').val(); // Selected employee ID
        const dateStart = $('#date_start').val(); // Start date input
        const dateEnd = $('#date_end').val(); // End date input
        const description = $('#project_description').val(); // Project description input
    
        try {
            const result = await rpc.query({
                route: '/my/employee-projects/create',
                params: {
                    name: projectName,
                    employee_id: parseInt(employeeId),
                    date_start: dateStart,
                    date_end: dateEnd,
                    description: description,
                },
            });

            if (result.success) {
                window.location.href = result.redirect_url;
            }

        } catch (error) {
            console.error('Error creating project:', error);
        }
    }
});

return {
    EmployeeProjectPortal: publicWidget.registry.EmployeeProjectPortal,
}
