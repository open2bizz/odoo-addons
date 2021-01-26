odoo.define('flow_calendar.CalendarQuickCreate', function(require) {
    "use strict";

    var core = require('web.core');
    var QuickCreate = require('web.CalendarQuickCreate');

    var _t = core._t;
    var QWeb = core.qweb;

    QuickCreate.include({
        events: {
            "click .flow-calendar-apps button": 'handle_click'
        },

        init: function(parent, buttons, options, dataTemplate, dataCalendar) {
            var self = this;
            this._super.apply(this, arguments);

            // this.btn_edit = this.$footer.find('button.btn-default:first');
            this.btn_edit = this.buttons[1];
            this.btn_edit.click = function (flow_calendar_model) {
                dataCalendar.flow_calendar_model = flow_calendar_model;
                dataCalendar.disableQuickCreate = true;
                dataCalendar.title = self.$('input').val().trim();
                dataCalendar.on_save = self.destroy.bind(self);
                self.trigger_up('openCreate', dataCalendar);
            };
        },

        handle_click: function(e) {
            var button = $(e.target)[0];
            this.dataTemplate.flow_calendar_model = $(button).next("input[name='flow_calendar_model']")[0].value;
            this.dataCalendar.flow_calendar_model = $(button).next("input[name='flow_calendar_model']")[0].value;
            
            var flow_calendar_model = $(button).next("input[name='flow_calendar_model']")[0].value;
            $(this.btn_edit).get(0).click(flow_calendar_model);
        }
    });
});
