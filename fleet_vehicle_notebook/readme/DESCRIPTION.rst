This module provides an empty notebook for the vehicle form.

This is a technical module and does not provide any new functionality.
Extend this module to add a page in the notebook section on the vehicle form related to the fleet application.

When extending the notepad in the vehicle form view, here is an example of how the code
would look like:


.. code:: xml

    <record id="fleet_vehicle_form_view" model="ir.ui.view">
        <field name="model">fleet_vehicle</field>
        <field name="inherit_id" ref="fleet.fleet_vehicle_view_form"/>
        <field name="arch" type="xml">
            <xpath expr="//notebook" position="inside">
                <page name="page_name" string="Page Name">
                    <field name="field_name"/>
                </page>
            </xpath>
        </field>
    </record>
