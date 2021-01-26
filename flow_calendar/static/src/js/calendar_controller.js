odoo.define('flow_calendar.CalendarController', function(require) {
    "use strict";

    var CalendarController = require('web.CalendarController');
    
    CalendarController.include({
        /**
         * @param {OdooEvent} event
         */
        _onOpenCreate: function (event) {
            this.context['default_flow_calendar_model'] = event.data.flow_calendar_model;
            this._super.apply(this, arguments);
        }
    });
});
