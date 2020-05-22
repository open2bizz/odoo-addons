     class SaleOrder(models.Model):
          _name = "sale.order"
          _inherit = ['sale.order', 'mail.thread', 'mail.activity.mixin']
